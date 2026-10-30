"""Trich xuat moi chuoi __() trong fork + doi chieu vi.csv (T101).

Nguon su that duy nhat cho so lieu i18n (khong so tay).
Chay tu root fork:  python sanpra_uiv16/tools/extract_i18n.py
In ra 3 so: distinct / covered / missing (+ danh sach missing kem file).
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

# R-01: brand terms giu tieng Anh, liet ke EXPLICIT (co bang chung tung chuoi).
# "Smart Education": ten thuong hieu, giu Anh (PM-SB-45 ap dung cho brand chung).
BRAND_WHITELIST = frozenset(
    {
        "Smart Education",
    }
)

SCAN_EXTENSIONS = (".js", ".py", ".html")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", "tools"}
# "tools": thu muc cong cu (chinh script nay) khong phai UI — khong quet de
# tranh tu-dem-chinh-minh (false positive "'...'" trong argparse).

CALL_RE = re.compile(r"(?<![\w_])__\(\s*['\"]([^'\"]+)['\"]")


def iter_source_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in SCAN_EXTENSIONS:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def extract_calls(root: Path):
    """Tra ve [(chuoi, file_tuong_doi)] cho moi luot goi __('...')."""
    calls = []
    root = Path(root)
    for path in iter_source_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for match in CALL_RE.finditer(text):
            calls.append((match.group(1), str(path.relative_to(root))))
    return calls


def load_covered(csv_path: Path):
    """Doc cot 0 cua vi.csv theo chuan CSV (quote-aware)."""
    covered = set()
    with open(csv_path, encoding="utf-8", newline="") as handle:
        for row in csv.reader(handle):
            if row and row[0].strip():
                covered.add(row[0])
    return covered


def compute_report(root: Path, csv_path: Path | None = None):
    """Tra ve dict distinct/covered/missing/missing_list/missing_files."""
    root = Path(root)
    if csv_path is None:
        csv_path = root / "sanpra_uiv16" / "translations" / "vi.csv"
    calls = extract_calls(root)
    by_string: dict[str, set[str]] = {}
    for text, relfile in calls:
        by_string.setdefault(text, set()).add(relfile)
    distinct = sorted(by_string)
    covered = load_covered(csv_path) if Path(csv_path).exists() else set()
    missing = [s for s in distinct if s not in covered]
    return {
        "distinct": len(distinct),
        "covered": len([s for s in distinct if s in covered]),
        "missing": len(missing),
        "missing_list": missing,
        "missing_files": {s: sorted(by_string[s]) for s in missing},
    }


def apply_whitelist(report: dict):
    """Tru brand terms (R-01) khoi missing; missing=0 chi cong nhan sau buoc nay."""
    missing_list = list(report.get("missing_list", []))
    whitelisted = [s for s in missing_list if s in BRAND_WHITELIST]
    remaining = [s for s in missing_list if s not in BRAND_WHITELIST]
    adjusted = dict(report)
    adjusted["whitelisted"] = whitelisted
    adjusted["missing_list"] = remaining
    adjusted["missing"] = len(remaining)
    return adjusted


def main(argv=None):
    parser = argparse.ArgumentParser(description="Trich __() + doi chieu vi.csv (T101)")
    parser.add_argument("--root", default=".", help="root fork (mac dinh: thu muc hien tai)")
    args = parser.parse_args(argv)
    report = compute_report(Path(args.root))
    print(f"distinct: {report['distinct']}")
    print(f"covered: {report['covered']}")
    print(f"missing: {report['missing']}")
    for text in report["missing_list"]:
        files = ", ".join(report["missing_files"][text][:3])
        print(f"  MISSING: {text!r} ({files})")
    adjusted = apply_whitelist(report)
    if adjusted["whitelisted"]:
        print(f"whitelisted (brand, khong tinh): {len(adjusted['whitelisted'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
