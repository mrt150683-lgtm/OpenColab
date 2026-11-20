#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data
cd data
base=https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion
while read -r sha file; do
  if ! [ -f "$file" ]; then
    curl --fail --location --retry 2 "$base/$file" --output "$file.part"
    printf '%s  %s\n' "$sha" "$file.part" | sha256sum --check
    mv "$file.part" "$file"
  fi
  printf '%s  %s\n' "$sha" "$file" | sha256sum --check
done <<'HASHES'
346e55b948d973a97e58d2351dde16a484bd415d4595297633bb08f03db6a073 t10k-images-idx3-ubyte.gz
67da17c76eaffca5446c3361aaab5c3cd6d1c2608764d35dfb1850b086bf8dd5 t10k-labels-idx1-ubyte.gz
3aede38d61863908ad78613f6a32ed271626dd12800ba2636569512369268a84 train-images-idx3-ubyte.gz
a04f17134ac03560a47e3764e11b92fc97de4d1bfaf8ba1a3aa29af54cc90845 train-labels-idx1-ubyte.gz
HASHES
