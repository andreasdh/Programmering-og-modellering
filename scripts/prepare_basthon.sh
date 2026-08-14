#!/usr/bin/env bash
set -Eeuo pipefail

out="${1:-_build/html/basthon}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

valid() {
  [[ -f "$1/index.html" ]] && [[ -d "$1/assets" ]] &&
    find "$1/assets" -maxdepth 1 -type f -name 'main.*.js' ! -name '*.map' -print -quit | grep -q .
}

install_dir() {
  rm -rf "$out"
  mkdir -p "$out"
  cp -a "$1/." "$out/"
}

from_pages() {
  echo "Trying Basthon from origin/gh-pages"
  mkdir -p "$tmp/pages"
  git fetch origin gh-pages --depth=1 || return 1
  git archive --format=tar origin/gh-pages basthon 2>/dev/null |
    tar -xf - -C "$tmp/pages" 2>/dev/null || return 1
  valid "$tmp/pages/basthon" || return 1
  install_dir "$tmp/pages/basthon"
}

from_download() {
  echo "Downloading Basthon from the official server"
  archive="$tmp/basthon-console.tgz"
  curl --fail --location --silent --show-error \
    --retry 5 --retry-all-errors --retry-delay 5 \
    --connect-timeout 20 --max-time 240 \
    -o "$archive" https://console.basthon.fr/basthon-console.tgz
  tar -tzf "$archive" >/dev/null
  mkdir -p "$tmp/download"
  tar -xzf "$archive" -C "$tmp/download"
  valid "$tmp/download"
  install_dir "$tmp/download"
}

mkdir -p "$out"
if from_pages; then
  source_name="gh-pages"
elif from_download; then
  source_name="official download"
else
  echo "Could not prepare Basthon" >&2
  exit 1
fi

basthon_js=$(find "$out/assets" -maxdepth 1 -type f -name 'main.*.js' ! -name '*.map' -print -quit)
test -n "$basthon_js"
python "$root/scripts/customize_basthon.py" "$out/index.html" "$basthon_js"

examples_dir="$root/docs/_static/basthon_examples"
[[ -d "$examples_dir" ]] || { echo "No Basthon examples found" >&2; exit 1; }
rm -rf "$out/examples"
mkdir -p "$out/examples"
cp -a "$examples_dir/." "$out/examples/"

echo "Basthon ready from $source_name"
