import json, csv, sys, os
from openpyxl import load_workbook
from pathlib import Path

SRC = Path("/Volumes/AI External/Nisamina_ai_Claude")
OUT = Path("/Volumes/AI External/Nisamina_ai_Claude/nisamina-app/10_ingest/extracted")

# 1. new_garifuna_words_expert_processed.ods → JSONL
# openpyxl doesn't read .ods. Use pyexcel-ods3 or pandas. Try pandas with odf engine.
try:
    import pandas as pd
    df = pd.read_excel(SRC / "new_garifuna_words_expert_processed.ods", engine="odf")
    print(f"ODS columns: {list(df.columns)}")
    print(f"ODS rows: {len(df)}")
    out_path = OUT / "ods_csv/new_garifuna_words.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            rec = {k: (None if pd.isna(v) else v) for k, v in row.items()}
            f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
    print(f"WROTE: {out_path} ({len(df)} rows)")
except Exception as e:
    print(f"ODS FAIL: {e}")

# 2. lgd_new_headwords_from_examples.csv → copy + JSONL
import shutil
csv_in = SRC / "lgd_new_headwords_from_examples.csv"
csv_out = OUT / "ods_csv/lgd_new_headwords.csv"
shutil.copy(csv_in, csv_out)
jsonl_out = OUT / "ods_csv/lgd_new_headwords.jsonl"
rows = 0
with open(csv_in, encoding="utf-8") as f, open(jsonl_out, "w", encoding="utf-8") as g:
    reader = csv.DictReader(f)
    for row in reader:
        g.write(json.dumps(row, ensure_ascii=False) + "\n")
        rows += 1
print(f"WROTE: {csv_out} + {jsonl_out} ({rows} rows)")

# 3. _COMBINED_DEDUPLICATED_REPORT verified-sentences JSON → copy + flatten
combined_src = SRC / "_COMBINED_DEDUPLICATED_REPORT_2026-05-18"
verified_in = combined_src / "verified_sentences_corpus_combined_deduplicated_2026-05-18.json"
verified_out = OUT / "combined_report/verified_sentences.json"
shutil.copy(verified_in, verified_out)
data = json.load(open(verified_in, encoding="utf-8"))
if isinstance(data, list):
    print(f"verified_sentences.json: list of {len(data)} records")
elif isinstance(data, dict):
    print(f"verified_sentences.json: dict with keys {list(data.keys())[:8]}")
    # If it has a list value try to count
    for k, v in data.items():
        if isinstance(v, list):
            print(f"  {k}: list len {len(v)}")

# 4. LGD attribution ledger
lgd_attr_in = combined_src / "garifuna_living_dictionary_attribution_ledger.csv"
lgd_attr_out = OUT / "combined_report/lgd_attribution.csv"
shutil.copy(lgd_attr_in, lgd_attr_out)
lgd_attr_rows = 0
with open(lgd_attr_in, encoding="utf-8") as f:
    reader = csv.reader(f)
    for _ in reader:
        lgd_attr_rows += 1
print(f"WROTE: lgd_attribution.csv ({lgd_attr_rows} rows including header)")

# 5. output_manifest.json
output_manifest_in = combined_src / "output_manifest.json"
output_manifest_out = OUT / "combined_report/output_manifest.json"
shutil.copy(output_manifest_in, output_manifest_out)
print(f"WROTE: output_manifest.json")
