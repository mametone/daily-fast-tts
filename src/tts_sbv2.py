"""
Style-Bert-VITS2 用 TTS クライアント。
公式 server_fastapi.py の GET/POST /voice を想定。base_url やパラメータは config / 環境変数で切り替え可能。

他の実装への対応:
- server_editor.py 由来の /api/... や hideyuda 版・Zenn の sbv2_api 等は、
  SBV2_BASE_URL と SBV2_ENDPOINT を変更するだけで同じクライアントで叩けます。
  例: SBV2_ENDPOINT=/api/tts や /voice のままポートだけ変える等。
"""
import logging
from pathlib import Path

from .config import (
    SBV2_BASE_URL,
    SBV2_ENDPOINT,
    SBV2_METHOD,
    SBV2_MODEL_NAME,
    SBV2_PARAMS,
    SBV2_SPEAKER_NAME,
    SBV2_TIMEOUT,
)
from .tts_base import TextToSpeechEngine

logger = logging.getLogger(__name__)


def _request_wav(text: str) -> bytes:
    """SBV2 /voice API を呼び出し、WAV バイト列を返す。接続失敗時はメッセージを付けて例外を投げる。"""
    try:
        import requests
    except ImportError:
        raise ImportError(
            "SBV2 エンジンを使うには requests をインストールしてください: pip install requests"
        ) from None

    url = f"{SBV2_BASE_URL.rstrip('/')}{SBV2_ENDPOINT}"
    params = {**SBV2_PARAMS, "text": text}
    if SBV2_MODEL_NAME is not None:
        params["model_name"] = SBV2_MODEL_NAME
    if SBV2_SPEAKER_NAME is not None:
        params["speaker_name"] = SBV2_SPEAKER_NAME

    try:
        if SBV2_METHOD == "POST":
            resp = requests.post(url, params=params, timeout=SBV2_TIMEOUT)
        else:
            resp = requests.get(url, params=params, timeout=SBV2_TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.ConnectError as e:
        logger.error("SBV2 サーバーに接続できません: %s", url)
        raise RuntimeError(
            "Style-Bert-VITS2 サーバーが起動していないか、接続できません。"
            " SBV2_BASE_URL（例: http://127.0.0.1:5000）を確認し、サーバーを起動してください。"
        ) from e
    except requests.exceptions.Timeout as e:
        logger.error("SBV2 リクエストがタイムアウトしました（%s 秒）: %s", SBV2_TIMEOUT, url)
        raise RuntimeError(
            f"Style-Bert-VITS2 サーバーへのリクエストがタイムアウトしました（{SBV2_TIMEOUT}秒）。"
            " サーバーが起動しているか、SBV2_BASE_URL を確認してください。"
        ) from e
    except requests.exceptions.HTTPError as e:
        logger.error("SBV2 API エラー: %s %s", resp.status_code, e)
        raise RuntimeError(
            f"Style-Bert-VITS2 API エラー: {e}. "
            "model_id / speaker_id / style 等のパラメータを確認してください。"
        ) from e

    return resp.content


def _play_wav_bytes(wav_bytes: bytes) -> None:
    """WAV バイト列を即時再生する。pydub を使用。"""
    try:
        from pydub import AudioSegment
        from pydub.playback import play
    except ImportError:
        raise ImportError(
            "SBV2 の即時再生には pydub をインストールしてください: pip install pydub. "
            "再生には ffmpeg または simpleaudio が必要です。"
        ) from None

    segment = AudioSegment.from_file(__import__("io").BytesIO(wav_bytes), format="wav")
    play(segment)


class Sbv2TtsEngine(TextToSpeechEngine):
    """
    Style-Bert-VITS2 の /voice API を叩く TTS エンジン。
    base_url やパラメータは config.py / 環境変数で変更可能。サーバー未起動時は明確なエラーメッセージを出す。
    """

    def speak(self, text: str) -> None:
        wav_bytes = _request_wav(text)
        _play_wav_bytes(wav_bytes)

    def synth_and_save(self, text: str, path: str) -> None:
        wav_bytes = _request_wav(text)
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        path_obj.write_bytes(wav_bytes)


# 後方互換: 既存の main が StyleBertVITS2Engine を参照しているためエイリアスを残す
StyleBertVITS2Engine = Sbv2TtsEngine
