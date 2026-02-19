"""
pyttsx3 を使った軽量TTS実装。
config の rate / volume / 音声ID を適用。音声ID未指定時は日本語を名前で自動選択。
"""
import logging
from pathlib import Path

import pyttsx3

from .config import DEFAULT_RATE, DEFAULT_VOLUME, PYTTSX3_VOICE_ID
from .tts_base import TextToSpeechEngine

logger = logging.getLogger(__name__)


def _select_japanese_voice(engine: pyttsx3.Engine) -> None:
    """利用可能な音声から日本語を優先して設定する。"""
    voices = engine.getProperty("voices")
    for voice in voices:
        name = (voice.name or "").lower()
        id_ = (voice.id or "").lower()
        if "japanese" in name or "japan" in name or "mei" in id_ or "mei" in name:
            engine.setProperty("voice", voice.id)
            return
    # 日本語が見つからなければ最初の音声のまま（フォールバック）
    logger.debug("日本語音声が見つからず、デフォルト音声を使用します")


class Pyttsx3Engine(TextToSpeechEngine):
    """pyttsx3 による TextToSpeechEngine 実装。"""

    def __init__(
        self,
        rate: int | None = None,
        volume: float | None = None,
        voice_id: str | None = None,
    ) -> None:
        self._rate = rate if rate is not None else DEFAULT_RATE
        self._volume = volume if volume is not None else DEFAULT_VOLUME
        self._voice_id = voice_id if voice_id is not None else PYTTSX3_VOICE_ID
        self._engine: pyttsx3.Engine | None = None

    def _get_engine(self) -> pyttsx3.Engine:
        if self._engine is None:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self._rate)
            self._engine.setProperty("volume", self._volume)
            if self._voice_id:
                self._engine.setProperty("voice", self._voice_id)
            else:
                _select_japanese_voice(self._engine)
        return self._engine

    def speak(self, text: str) -> None:
        engine = self._get_engine()
        engine.say(text)
        engine.runAndWait()

    def synth_and_save(self, text: str, path: str) -> None:
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        engine = self._get_engine()
        engine.save_to_file(text, str(path_obj))
        engine.runAndWait()
