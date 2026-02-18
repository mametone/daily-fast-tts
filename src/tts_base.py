"""
TTSエンジン共通インターフェース。
pyttsx3 / Style-Bert-VITS2 などはこのインターフェースを実装して差し替え可能にする。
"""
from abc import ABC, abstractmethod


class TextToSpeechEngine(ABC):
    """テキストを音声に変換し、再生またはファイル保存するエンジンの抽象基底クラス。"""

    @abstractmethod
    def speak(self, text: str) -> None:
        """テキストを即時再生する。ブロックし、再生が終わるまで戻らない。"""
        ...

    @abstractmethod
    def synth_and_save(self, text: str, path: str) -> None:
        """テキストを音声に合成し、指定パスにWAV等で保存する。"""
        ...
