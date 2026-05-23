#!/usr/bin/env bash
# M-P1.F.svg_curriculum — paste-and-run SVG curriculum ingest
# Per F-050 spec. Run from any terminal; 22 PDFs; <5 min wall-clock.
# Per SVG Copyright Act 2003 §54 educational-use provisions + svgcdu.org +
# gov.vc public PDFs.

set -euo pipefail

OUT="/Volumes/AI External/Nisamina_ai_Claude/nisamina-app/50_app/lms/svg_yurumein/curriculum_source"
LEDGER="/Volumes/AI External/Nisamina_ai_Claude/nisamina-app/50_app/lms/svg_yurumein/attribution/SVG_ACQUISITION_LEDGER.md"
mkdir -p "$OUT"

# Initialize ledger
{
  echo "# SVG / Yurumein Curriculum Acquisition Ledger"
  echo ""
  echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Per M-P1.F.svg_curriculum + F-050 + SVG Copyright Act 2003 §54 educational-use"
  echo ""
  echo "## Acquisition table"
  echo ""
  echo "| # | URL | Local | SHA256 (head) | Bytes |"
  echo "|---|---|---|---|---:|"
} > "$LEDGER"

# URL list: place at $OUT/SVG_URLS.txt (one URL per line; ~22 entries
# per F-050 spec). Director can populate from supervisor brief
# nisamina-supervisor/notes/2026-05-23_S15_svg_curriculum_ingest_spec.md §3.

if [ ! -f "${OUT}/SVG_URLS.txt" ]; then
  echo "MISSING: ${OUT}/SVG_URLS.txt" >&2
  echo "Populate the file with one URL per line (from supervisor S15 SVG spec §3)" >&2
  echo "then re-run this script." >&2
  exit 1
fi

i=0
while IFS= read -r url; do
  [ -z "$url" ] && continue
  [[ "$url" =~ ^# ]] && continue
  i=$((i+1))
  fname=$(basename "${url%\?*}")
  local_path="${OUT}/${fname}"
  echo "[${i}] Downloading: $url"
  if ! curl -fsS -o "$local_path" --max-time 60 "$url"; then
    echo "WARN: download failed for $url" >&2
    continue
  fi
  sha=$(shasum -a 256 "$local_path" | cut -d' ' -f1)
  bytes=$(wc -c < "$local_path" | tr -d ' ')
  echo "| ${i} | ${url} | ${fname} | ${sha:0:16}... | ${bytes} |" >> "$LEDGER"
done < "${OUT}/SVG_URLS.txt"

# Extract text from each PDF
extracted=0
for pdf in "$OUT"/*.pdf; do
  [ ! -f "$pdf" ] && continue
  txt="${pdf%.pdf}.txt"
  if pdftotext -layout "$pdf" "$txt" 2>/dev/null; then
    extracted=$((extracted+1))
  else
    echo "WARN: pdftotext failed on $pdf" >&2
  fi
done

echo ""
echo "----------------------------------------------------------------------"
echo "SVG curriculum ingest complete."
echo "Downloaded:   $i files"
echo "Extracted:    $extracted text files"
echo "Ledger:       $LEDGER"
echo "Next steps:   engineer appends EXTRACTION_MANIFEST + 6 attribution rows"
echo "              + Commission consultation on TK Labels for Yurumein content"
echo "----------------------------------------------------------------------"
