"""
設定: 音声速度・音量・デフォルトエンジン・最小文字数など。
pyttsx3: rate / volume / 音声ID をここまたは環境変数で変更可能。
SBV2 用の base_url やパラメータは環境変数で上書き可能。
"""
import os
from pathlib import Path

# ----- pyttsx3 用 -----
# 読み上げ速度（pyttsx3 の rate: デフォルト約200。大きいほど速い）
DEFAULT_RATE = int(os.environ.get("PYTTSX3_RATE", "250"))

# 音量 0.0〜1.0
DEFAULT_VOLUME = float(os.environ.get("PYTTSX3_VOLUME", "1.0"))

# 優先する音声ID（None のときは日本語ボイスを名前で自動選択）
# 例: "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\..." (Windows)
#      Linux では espeak の voice id を指定可能
PYTTSX3_VOICE_ID = os.environ.get("PYTTSX3_VOICE_ID", None)

# クリップボードのテキストがこの文字数未満なら読み上げない（短文スキップ）
MIN_TEXT_LENGTH = 10

# 使用するTTSエンジン: "pyttsx3" | "sbv2"（環境変数 DEFAULT_ENGINE で上書き可）
_engine = os.environ.get("DEFAULT_ENGINE", "pyttsx3")
DEFAULT_ENGINE = _engine if _engine in ("pyttsx3", "sbv2") else "pyttsx3"

# プロジェクトルート（config.py から見たルート）
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Style-Bert-VITS2 API 用設定（server_fastapi.py の /voice を想定）
# 将来 SBV2 を有効にする場合、ユーザーが埋める主な項目:
#   - SBV2_BASE_URL: サーバー起動後の URL（例: http://127.0.0.1:5000）
#   - SBV2_SPEAKER_ID / SBV2_SPEAKER_NAME: 話者
#   - SBV2_MODEL_ID / SBV2_MODEL_NAME: モデル
#   - SBV2_LENGTH: 話速（大きいほど遅い）
#   - SBV2_LANGUAGE: 言語（日本語は JP）
#   - SBV2_STYLE / SBV2_STYLE_WEIGHT: スタイル（サーバー対応時）
# ---------------------------------------------------------------------------
SBV2_BASE_URL = os.environ.get("SBV2_BASE_URL", "http://127.0.0.1:5000")
SBV2_ENDPOINT = os.environ.get("SBV2_ENDPOINT", "/voice")
SBV2_TIMEOUT = int(os.environ.get("SBV2_TIMEOUT", "30"))
# 推奨: POST（GET は長文で URL 制限に引っかかるため server_fastapi も POST 推奨）
SBV2_METHOD = os.environ.get("SBV2_METHOD", "POST").upper()

# /voice に渡すクエリ or JSON パラメータ（サーバー構築後に調整）
# 数値は環境変数 SBV2_LENGTH 等で上書き可能（例: SBV2_LENGTH=1.2）
SBV2_PARAMS = {
    "model_id": int(os.environ.get("SBV2_MODEL_ID", "0")),
    "speaker_id": int(os.environ.get("SBV2_SPEAKER_ID", "0")),
    "sdp_ratio": float(os.environ.get("SBV2_SDP_RATIO", "0.2")),
    "noise": float(os.environ.get("SBV2_NOISE", "0.6")),
    "noisew": float(os.environ.get("SBV2_NOISEW", "0.8")),
    "length": float(os.environ.get("SBV2_LENGTH", "1.0")),
    "language": os.environ.get("SBV2_LANGUAGE", "JP"),
    "auto_split": os.environ.get("SBV2_AUTO_SPLIT", "true").lower() in ("true", "1", "yes"),
    "style": os.environ.get("SBV2_STYLE", "Neutral"),
    "style_weight": float(os.environ.get("SBV2_STYLE_WEIGHT", "0.7")),
}
# 文字列で渡すもの（model_name, speaker_name はサーバー側に合わせて必要なら設定）
SBV2_MODEL_NAME = os.environ.get("SBV2_MODEL_NAME", None)  # 指定時は model_id より優先
SBV2_SPEAKER_NAME = os.environ.get("SBV2_SPEAKER_NAME", None)  # 指定時は speaker_id より優先
