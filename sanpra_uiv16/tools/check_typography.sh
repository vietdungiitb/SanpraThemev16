#!/usr/bin/env bash
# check_typography.sh — quet rule font-size 7px/8px con sot trong Studio CSS (T201).
#
# Dung:  bash sanpra_uiv16/tools/check_typography.sh [--self-test] [css-file...]
# Mac dinh quet sanpra_uiv16/public/css/theme_studio.css (tu root fork).
# Exit: 0 = 0 rule vi pham; 1 = con sot; 2 = sai tham so.
#
# R1: pattern bat moi rule chu <11px (muc tieu T201): font-size 6-10px VA shorthand font:<...>6-10px.
set -u

HIT_RE='font(-size)?:[^;{}]*\b(6|7|8|9|10)px'

self_test() {
  local rc=0 tmp
  tmp="$(mktemp -d)"
  printf '.a { font-size: 8px; }\n' > "$tmp/bad1.css"
  printf '.b { font: 650 7px sans-serif; }\n' > "$tmp/bad2.css"
  printf ".e { font-size: 10px; }" > "$tmp/bad3.css"
  printf '.c { font-size: 11px; }\n.d { font-size: 12px; }\n' > "$tmp/good.css"
  if bash "$0" "$tmp/bad1.css" >/dev/null 2>&1; then
    echo "[self-test] FAIL: font-size 8px ma van exit 0"; rc=1;
  else
    echo "[self-test] OK: font-size 8px -> exit != 0";
  fi
  if bash "$0" "$tmp/bad3.css" >/dev/null 2>&1; then
    echo "[self-test] FAIL: font-size 10px ma van exit 0"; rc=1;
  else
    echo "[self-test] OK: font-size 10px -> exit != 0";
  fi
  if bash "$0" "$tmp/bad2.css" >/dev/null 2>&1; then
    echo "[self-test] FAIL: shorthand 7px ma van exit 0"; rc=1;
  else
    echo "[self-test] OK: shorthand 7px -> exit != 0";
  fi
  if bash "$0" "$tmp/good.css" >/dev/null 2>&1; then
    echo "[self-test] OK: CSS sach -> exit 0";
  else
    echo "[self-test] FAIL: CSS sach ma exit != 0"; rc=1;
  fi
  rm -rf "$tmp"
  return "$rc"
}

if [ "${1:-}" = "--self-test" ]; then
  self_test
  exit "$?"
fi

files=("$@")
if [ "${#files[@]}" -eq 0 ]; then
  files=("sanpra_uiv16/public/css/theme_studio.css")
fi

hits=0
for f in "${files[@]}"; do
  if [ ! -f "$f" ]; then
    echo "thieu file: $f" >&2
    exit 2
  fi
  # shellcheck disable=SC2002
  while IFS= read -r line; do
    hits=$((hits + 1))
    echo "$line"
  done < <(grep -nE "$HIT_RE" "$f" || true)
done

if [ "$hits" -gt 0 ]; then
  echo "con $hits rule chu duoi 11px"
  exit 1
fi
echo "0 rule vi pham"
exit 0
