# daily-fast-tts

ブラウザなどで**選択してコピーした日本語テキスト**を、ローカルTTSで**高速に読み上げる**ためのツールです。  
「選択 → Ctrl+C → ホットキー」の最小操作で耳読みできることを目指しています。ファイルを開く手間は極力なくし、基本は**即時再生**、必要に応じてオプションで保存できます。

- **完全ローカル・無料**で動作
- 日本語のナチュラルさと**高速再生**（読み上げ速度を高めに設定可能）を重視
- 入力: クリップボードのテキスト（選択してコピー済み）
- 出力: デフォルトはそのまま再生／オプションで WAV 保存

設計メモやAIとの壁打ち記録は [Notion: 日常高速TTS](https://www.notion.so/TTS-30b7c88ab54d800dbb6bf2a85440207c) に置いています。

---

## セットアップ

- Python 3.10 以上を推奨（pyenv や venv で環境を分けるとよいです）

```bash
cd /path/to/daily-fast-tts
python -m venv .venv
source .venv/bin/activate   # Windows の場合は .venv\Scripts\activate
pip install -r requirements.txt
```

- **Linux/WSL**: 音声出力に `espeak` や `libespeak` 等が必要な場合があります。日本語を優先するため、可能なら日本語対応の音声パッケージを入れてください。
- **Windows**: pyttsx3 は SAPI を使うため、日本語音声（例: 音声パック）が入っていればそのまま利用できます。

---

## 使い方

1. 読み上げたいテキストを選択して **Ctrl+C** でコピー
2. 次のいずれかで実行
   - `python -m src.main`
   - `./scripts/run_tts.sh`（WSL など。プロジェクトルートで実行）

クリップボードの内容が一定長以上なら即再生され、終了後はそのままプロセスが終わります。  
テキストが空または短すぎる場合は警告を出して即終了します。

### オプション

- **音声をファイルに保存する**: `python -m src.main --save output.wav`
- **エンジン指定**（現状は pyttsx3 のみ実装）: `python -m src.main --engine pyttsx3`

読み上げ速度・音量・最小文字数などは `src/config.py` で変更できます。

---

## プロジェクト構成（案）

```
daily-fast-tts/
├── src/
│   ├── main.py          # エントリ: クリップボード → TTS → 再生
│   ├── config.py        # 設定（速度・音量・最小文字数・デフォルトエンジン）
│   ├── tts_base.py      # TTS エンジン共通インターフェース
│   ├── tts_pyttsx3.py   # pyttsx3 版（現在の実装）
│   └── tts_sbv2.py      # 将来の Style-Bert-VITS2 用（スケルトンのみ）
├── scripts/
│   └── run_tts.sh       # WSL から実行するスクリプト
├── README.md
└── requirements.txt
```

---

## 今後の予定

- **Style-Bert-VITS2** を統合し、高品質・高速な読み上げに差し替え可能にする予定です。  
  ローカルで API サーバーを立て、`tts_sbv2.py` から呼び出す形を想定しています。
- リファクタや設定の外部ファイル化（YAML/環境変数など）は必要に応じて追加します。
