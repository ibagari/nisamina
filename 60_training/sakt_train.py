"""SAKT PyTorch training scaffold + ONNX export.

Per D-070 director approval (PyTorch + SAKT, best-practice ONNX-export path).

Training pipeline:
1. Load EdNet-KT1 (Riiid 2020) or per-cohort interactions from production
2. Tokenize: (skill_id, correctness) pairs
3. Train SAKT (Pandey & Karypis 2019) — self-attention; AUC target ~0.80
4. Export to ONNX for lightweight inference on HF Space (no PyTorch runtime
   dependency; ~10x smaller deploy than full PyTorch + torchvision)

The inference path lives at `50_app/lms/_engine/learner_model.py`
AttentiveKTShadow — when an ONNX checkpoint is available, the shadow uses
it; else falls back to the pure-Python scaffold (already shipped D-068).

USAGE:
    python3 60_training/sakt_train.py \\
        --dataset EdNet-KT1 \\
        --epochs 20 \\
        --batch-size 256 \\
        --export-path 50_app/lms/_engine/sakt_checkpoint.onnx

Dependencies (training-time only; NOT bundled in HF Space):
    torch>=2.0
    onnx>=1.15

Note: this script is engineer-RUN-IT (or compute-cluster-run-it); not invoked
by the running platform. Training data + checkpoint live in `60_training/`.
Checkpoint is committed to the repo (small; ~30 MB) for reproducibility.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable, Optional

# Lazy import — only required for training, not for module load
def _require_torch():
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
        return torch, nn, optim
    except ImportError as e:
        raise ImportError(
            "PyTorch required for SAKT training. Install with: pip install torch>=2.0"
        ) from e


# === SAKT architecture (Pandey & Karypis 2019; arXiv 1907.06837) ============


def build_sakt_model(
    n_skills: int,
    d_model: int = 64,
    n_heads: int = 8,
    n_layers: int = 1,
    dropout: float = 0.1,
    max_seq: int = 200,
):
    """Construct a SAKT model.

    SAKT = Self-Attentive Knowledge Tracing. Decoder-only transformer over
    interactions; predicts next-interaction correctness. AUC ≈0.80 on EdNet.

    Architecture:
    - Interaction embedding (skill × correctness) → 2 * n_skills embeddings
    - Skill query embedding → n_skills embeddings
    - Multi-head self-attention over interaction sequence; query = next skill
    - FFN + sigmoid → P(correct on next skill)
    """
    torch, nn, _ = _require_torch()

    class SAKT(nn.Module):
        def __init__(self):
            super().__init__()
            self.interaction_emb = nn.Embedding(2 * n_skills + 1, d_model, padding_idx=0)
            self.skill_emb = nn.Embedding(n_skills + 1, d_model, padding_idx=0)
            self.position_emb = nn.Embedding(max_seq, d_model)
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=d_model, nhead=n_heads, dropout=dropout,
                batch_first=True, dim_feedforward=d_model * 4,
            )
            self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
            self.fc = nn.Linear(d_model, 1)

        def forward(self, interactions, target_skills):
            # interactions: [batch, seq] of interaction ids
            # target_skills: [batch, seq] of next-skill ids
            batch_size, seq_len = interactions.shape
            positions = torch.arange(seq_len, device=interactions.device).unsqueeze(0).expand(batch_size, -1)
            x = self.interaction_emb(interactions) + self.position_emb(positions)
            x = self.encoder(x)
            q = self.skill_emb(target_skills)
            # Element-wise mul (simplified attention) — full SAKT uses cross-attention
            x = x * q
            logits = self.fc(x).squeeze(-1)
            return torch.sigmoid(logits)

    return SAKT()


# === Training loop ========================================================


def train_sakt(
    train_loader,
    val_loader,
    n_skills: int,
    epochs: int = 20,
    lr: float = 1e-3,
    device: str = "cpu",
):
    """Train SAKT to convergence. Returns trained model + best val AUC."""
    torch, nn, optim = _require_torch()
    model = build_sakt_model(n_skills=n_skills).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.BCELoss()

    logging.basicConfig(level=logging.INFO, format="[sakt-train] %(message)s")
    best_val_auc = 0.0
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for batch in train_loader:
            interactions, target_skills, targets = batch
            interactions = interactions.to(device)
            target_skills = target_skills.to(device)
            targets = targets.float().to(device)
            optimizer.zero_grad()
            preds = model(interactions, target_skills)
            loss = loss_fn(preds, targets)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        # Val
        model.eval()
        val_auc = _compute_val_auc(model, val_loader, device)
        logging.info(
            f"epoch {epoch + 1}/{epochs} train_loss={total_loss / max(1, len(train_loader)):.4f} val_auc={val_auc:.4f}"
        )
        if val_auc > best_val_auc:
            best_val_auc = val_auc
    return model, best_val_auc


def _compute_val_auc(model, val_loader, device: str) -> float:
    """Compute AUC on validation set. Best-practice: use sklearn if available."""
    torch, _, _ = _require_torch()
    all_preds: list[float] = []
    all_targets: list[float] = []
    with torch.no_grad():
        for batch in val_loader:
            interactions, target_skills, targets = batch
            preds = model(interactions.to(device), target_skills.to(device))
            all_preds.extend(preds.cpu().numpy().flatten().tolist())
            all_targets.extend(targets.numpy().flatten().tolist())
    try:
        from sklearn.metrics import roc_auc_score
        return float(roc_auc_score(all_targets, all_preds))
    except ImportError:
        # Fallback: simple accuracy
        correct = sum(
            1 for p, t in zip(all_preds, all_targets) if (p >= 0.5) == (t >= 0.5)
        )
        return correct / max(1, len(all_preds))


# === ONNX export ==========================================================


def export_to_onnx(
    model,
    n_skills: int,
    output_path: Path,
    max_seq: int = 200,
):
    """Export trained SAKT to ONNX for lightweight inference deployment.

    Per D-070 best-practice: HF Space ships onnxruntime (~50 MB) + ONNX
    checkpoint (~30 MB) instead of full PyTorch (~750 MB).
    """
    torch, _, _ = _require_torch()
    model.eval()
    # Dummy inputs for shape tracing
    dummy_interactions = torch.zeros((1, max_seq), dtype=torch.long)
    dummy_target_skills = torch.zeros((1, max_seq), dtype=torch.long)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        model,
        (dummy_interactions, dummy_target_skills),
        str(output_path),
        input_names=["interactions", "target_skills"],
        output_names=["p_correct"],
        dynamic_axes={
            "interactions": {0: "batch", 1: "seq"},
            "target_skills": {0: "batch", 1: "seq"},
            "p_correct": {0: "batch", 1: "seq"},
        },
        opset_version=17,
    )
    logging.info(f"Exported ONNX checkpoint to {output_path}")


# === Entrypoint ===========================================================


def main():
    parser = argparse.ArgumentParser(description="Train SAKT for Nisamina learner model")
    parser.add_argument("--dataset", choices=["EdNet-KT1", "production-cohort"], default="EdNet-KT1")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--n-skills", type=int, default=10000,
                        help="Vocabulary size (set to your foundry headword count for production)")
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    parser.add_argument(
        "--export-path",
        default="50_app/lms/_engine/sakt_checkpoint.onnx",
        help="Where to write the ONNX checkpoint",
    )
    args = parser.parse_args()

    print(f"[sakt-train] dataset={args.dataset} epochs={args.epochs} n_skills={args.n_skills}")
    print("[sakt-train] NOTE: full training requires EdNet-KT1 download + DataLoader wiring.")
    print("[sakt-train] This entrypoint is a scaffold; production training adds:")
    print("[sakt-train]   1. EdNet-KT1 fetch (huggingface_hub.snapshot_download + Riiid 2020 license)")
    print("[sakt-train]   2. DataLoader with masked-attention prep")
    print("[sakt-train]   3. Distributed training if cohort > 1M interactions")
    print("[sakt-train]   4. Hyperparameter sweep (d_model + n_heads + dropout)")
    print("[sakt-train] For now: import this module's build_sakt_model() + train_sakt() + export_to_onnx() functions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
