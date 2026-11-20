#!/bin/sh
# emdash-harper - Harper grammar-check plugin bridge for EmDash.
# Uses harper-ls (LSP, bundled in the Newsk image) or harper-cli if present.
# Usage: emdash-harper check FILE
set -e
if [ "$1" != "check" ] || [ -z "$2" ]; then
  echo "usage: emdash-harper check FILE" >&2
  exit 1
fi
if command -v harper-cli >/dev/null 2>&1; then
  exec harper-cli lint "$2"
elif command -v harper-ls >/dev/null 2>&1; then
  # harper-ls speaks LSP over stdio; editors drive it directly.
  exec harper-ls --stdio
else
  echo "emdash-harper: neither harper-cli nor harper-ls found" >&2
  exit 1
fi