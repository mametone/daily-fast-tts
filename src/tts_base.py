"""
TTSエンジン共通インターフェース。
pyttsx3 / Style-Bert-VITS2 などはこのインターフェースを実装して差し替え可能にする。
新しいエンジン（SBV2 以外の GPU エンジンなど）を追加する場合は、この抽象クラスを実装し、
main の get_engine() に名前を登録すればよい。接続先 URL やパラメータは各エンジンの config で扱う。
"""
from abc import ABC, abstractmethod


class TextToSpeechEngine(ABC):
    """
    テキストを音声に変換し、再生またはファイル保存するエンジンの抽象基底クラス。

    実装クラスが満たすこと:
    - speak(text): テキストを即時再生する。ブロックし、再生が終わるまで戻らない。
    - synth_and_save(text, path): テキストを音声に合成し、指定パスに WAV 等で保存する。

    設定（URL・話者・話速など）は各エンジンが config または環境変数から読み込む。
    """

    @abstractmethod
    def speak(self, text: str) -> None:
        """テキストを即時再生する。ブロックし、再生が終わるまで戻らない。"""
        ...

    @abstractmethod
    def synth_and_save(self, text: str, path: str) -> None:
        """テキストを音声に合成し、指定パスにWAV等で保存する。"""
        ...
