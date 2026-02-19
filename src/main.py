"""
エントリポイント: クリップボードのテキストを取得 → TTS → 再生（またはオプションで保存）。
実行例: python -m src.main
       python -m src.main --engine pyttsx3
       python -m src.main --save output.wav
"""
import argparse
import logging
import sys

import pyperclip

from .config import DEFAULT_ENGINE, MIN_TEXT_LENGTH
from .tts_base import TextToSpeechEngine
from .tts_pyttsx3 import Pyttsx3Engine
from .tts_sbv2 import StyleBertVITS2Engine

# 最低限のログ（pyttsx3 等の例外用）。レベルは WARNING でスタート
logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


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
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="ログを詳細に出す（デバッグ用）",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        text = pyperclip.paste()
    except Exception as e:
        logger.error("クリップボード取得エラー: %s", e)
        sys.exit(1)

    text = text.strip()
    if len(text) == 0:
        print("クリップボードが空です。読み上げたいテキストを選択してコピーしてください。", file=sys.stderr)
        sys.exit(1)
    if len(text) < MIN_TEXT_LENGTH:
        print(
            f"テキストが短すぎます（{len(text)}文字）。{MIN_TEXT_LENGTH}文字以上をコピーしてください。",
            file=sys.stderr,
        )
        sys.exit(1)

    engine = get_engine(args.engine)

    try:
        if args.save:
            engine.synth_and_save(text, args.save)
            print(f"保存しました: {args.save}")
        else:
            engine.speak(text)
    except RuntimeError as e:
        if "Style-Bert-VITS2" in str(e) or "SBV2" in str(e):
            print(str(e), file=sys.stderr)
            sys.exit(1)
        logger.error("TTS 実行エラー: %s", e)
        print(f"TTS エラー: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error("TTS 実行エラー: %s", e)
        if args.verbose:
            logger.exception("")
        print(f"TTS エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
