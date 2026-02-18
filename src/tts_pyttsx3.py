"""
pyttsx3 を使った軽量TTS実装。
日本語音声（Japanese / Mei 等）を自動選択し、config の rate/volume を適用する。
"""
from pathlib import Path

import pyttsx3

from .config import DEFAULT_RATE, DEFAULT_VOLUME
from .tts_base import TextToSpeechEngine


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


class Pyttsx3Engine(TextToSpeechEngine):
    """pyttsx3 による TextToSpeechEngine 実装。"""

    def __init__(
        self,
        rate: int = DEFAULT_RATE,
        volume: float = DEFAULT_VOLUME,
    ) -> None:
        self._rate = rate
        self._volume = volume
        self._engine: pyttsx3.Engine | None = None

    def _get_engine(self) -> pyttsx3.Engine:
        if self._engine is None:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self._rate)
            self._engine.setProperty("volume", self._volume)
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
