"""
設定: 音声速度・音量・デフォルトエンジン・最小文字数など。
設定ファイル（YAML/JSON）や環境変数で上書きする拡張は将来対応。
"""
from pathlib import Path

# 読み上げ速度（pyttsx3 の rate: デフォルト約200。大きいほど速い）
DEFAULT_RATE = 250

# 音量 0.0〜1.0
DEFAULT_VOLUME = 1.0

# クリップボードのテキストがこの文字数未満なら読み上げない（短文スキップ）
MIN_TEXT_LENGTH = 10

# 使用するTTSエンジン: "pyttsx3" | "sbv2"（将来）
DEFAULT_ENGINE = "pyttsx3"

# プロジェクトルート（config.py から見たルート）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
