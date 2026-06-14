"""Shared corpus loader with COALESCING dedupe.

Dedupe key = (final_url, "group|niche|keyword"). The old behaviour (latest-row-wins) let an
incomplete re-scan WIPE earlier enrichment: e.g. a burst run whose Semrush authority call
failed would overwrite the referring_domains we'd already paid for on an earlier run. This
loader instead keeps the most recent NON-NULL value per field, processing shards in
chronological order (filenames are timestamp-prefixed). So newer data wins where present,
but a null never erases a value we already have.

Use: from corpus_load import load
"""
import json
import glob
import os


def load(src):
    files = ([src] if os.path.exists(src) else [])
    files += sorted(glob.glob(os.path.join(os.path.dirname(src) or ".", "corpus", "*.jsonl")))
    merged = {}
    for fp in files:
        try:
            fh = open(fp, encoding="utf-8")
        except Exception:
            continue
        for line in fh:
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            p = r.get("label", "").split("|")
            key = ((r.get("final_url") or r.get("url")), "|".join(p[:3]))
            d = merged.setdefault(key, {})
            for k, v in r.items():
                if v is not None:        # never let a null overwrite a real value
                    d[k] = v
        fh.close()
    return list(merged.values())
