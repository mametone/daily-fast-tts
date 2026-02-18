#!/usr/bin/env bash
# WSL から daily-fast-tts を実行するスクリプト。
# 使い方: ./scripts/run_tts.sh
# または: ./scripts/run_tts.sh --save ./out.wav

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

if [ -n "$VIRTUAL_ENV" ]; then
  : # 既に venv 有効
elif [ -d ".venv" ]; then
  source .venv/bin/activate
fi

exec python -m src.main "$@"
