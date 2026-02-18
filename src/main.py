"""
エントリポイント: クリップボードのテキストを取得 → TTS → 再生（またはオプションで保存）。
実行例: python -m src.main
"""
import argparse
import sys

import pyperclip

from .config import DEFAULT_ENGINE, MIN_TEXT_LENGTH
from .tts_base import TextToSpeechEngine
from .tts_pyttsx3 import Pyttsx3Engine
from .tts_sbv2 import StyleBertVITS2Engine


def get_engine(name: str) -> TextToSpeechEngine:
    if name == "pyttsx3":
        return Pyttsx3Engine()
    if name == "sbv2":
        return StyleBertVITS2Engine()
    raise ValueError(f"不明なエンジン: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="クリップボードのテキストをローカルTTSで即再生（オプションで保存）"
    )
    parser.add_argument(
        "--save",
        metavar="PATH",
        default=None,
        help="音声を指定パスにWAV保存する（未指定なら再生のみ）",
    )
    parser.add_argument(
        "--engine",
        choices=("pyttsx3", "sbv2"),
        default=DEFAULT_ENGINE,
        help="使用するTTSエンジン（デフォルト: pyttsx3）",
    )
    args = parser.parse_args()

    try:
        text = pyperclip.paste()
    except Exception as e:
        print(f"クリップボード取得エラー: {e}", file=sys.stderr)
        sys.exit(1)

    text = text.strip()
    if len(text) < MIN_TEXT_LENGTH:
        print(
            f"テキストが短すぎます（{len(text)}文字）。{MIN_TEXT_LENGTH}文字以上をコピーしてください。",
            file=sys.stderr,
        )
        sys.exit(1)

    engine = get_engine(args.engine)

    if args.save:
        engine.synth_and_save(text, args.save)
        print(f"保存しました: {args.save}")
    else:
        engine.speak(text)


if __name__ == "__main__":
    main()
