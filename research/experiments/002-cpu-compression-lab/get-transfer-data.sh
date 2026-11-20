#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for d in mnist-data transfer-data; do
  mkdir -p "$d"
  case "$d" in
    mnist-data) base=https://storage.googleapis.com/cvdf-datasets/mnist ;;
    transfer-data) base=https://codh.rois.ac.jp/kmnist/dataset/kmnist ;;
  esac
  (cd "$d"
   while read -r sha file; do
     if [ ! -f "$file" ]; then
       curl -fLsS --retry 2 --max-time 120 "$base/$file" -o "$file.part"
       printf '%s  %s\n' "$sha" "$file.part" | sha256sum -c
       mv "$file.part" "$file"
     fi
     printf '%s  %s\n' "$sha" "$file" | sha256sum -c
   done < "../$d.sha256")
done
