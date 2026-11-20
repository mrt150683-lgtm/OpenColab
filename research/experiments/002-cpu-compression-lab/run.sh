#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-2}"
case "${1:-verify}" in
 verify) sha256sum -c MANIFEST.sha256; python summary.py ;;
 fashion)
    bash get-data.sh
    (cd lane_groups; python verify_codec.py; python confirm.py)
    (cd lane_residual; sha256sum -c freeze.sha256; python confirm.py)
    (cd lane_refit; python confirm.py; python dense_control.py)
    python summary.py ;;
 transfer)
    bash get-transfer-data.sh
    for d in mnist-data transfer-data; do
       for s in 101 103 107; do python transfer.py "$d" "$s"; done
    done
    python summary.py ;;
 *) echo "Use verify, fashion, or transfer" >&2; exit 2 ;;
esac
