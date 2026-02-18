"""
Style-Bert-VITS2 用 TTS スケルトン。
将来、ローカルで起動した Style-Bert-VITS2 API を呼び出す実装に差し替える。

Style-Bert-VITS2 API の URL やパラメータ（例: /tts_fn, model_name, length, language 等）
はここに書く予定。Notion の「日常高速TTS」ページや公式リポジトリを参照して実装する。
"""
from .tts_base import TextToSpeechEngine


class StyleBertVITS2Engine(TextToSpeechEngine):
    """Style-Bert-VITS2 API を利用する TTS エンジン（スケルトン）。"""

    def speak(self, text: str) -> None:
        raise NotImplementedError(
            "Style-Bert-VITS2 統合時: API で合成 → バイト列を pydub 等で再生"
        )

    def synth_and_save(self, text: str, path: str) -> None:
        raise NotImplementedError(
            "Style-Bert-VITS2 統合時: API で合成 → レスポンスを path に保存"
        )
