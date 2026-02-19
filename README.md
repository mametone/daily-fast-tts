# daily-fast-tts

ブラウザなどで**選択してコピーした日本語テキスト**を、ローカルTTSで**高速に読み上げる**ためのツールです。  
「選択 → Ctrl+C → ホットキー」の最小操作で耳読みできることを目指しています。ファイルを開く手間は極力なくし、基本は**即時再生**、必要に応じてオプションで保存できます。

設計メモやAIとの壁打ち記録は [Notion: 日常高速TTS](https://www.notion.so/TTS-30b7c88ab54d800dbb6bf2a85440207c) に置いています。

---

## 現時点でできること（pyttsx3）

- **完全ローカル・完全無料**の TTS：クラウド API や有料エンジンは一切使いません。
- **クリップボード読み上げ**：テキストを選択してコピー → コマンド実行で即再生。
- **設定で調整可能**：読み上げ速度（rate）、音量（volume）、優先する音声（日本語の自動選択、または音声ID指定）。
- **オプションで WAV 保存**：`--save` でファイルに書き出し可能。
- **エンジン切り替えの受け口**：`--engine pyttsx3`（デフォルト）／`--engine sbv2`（SBV2 サーバー利用時。サーバーは別途起動が必要）。

入力は**クリップボード専用**です（標準入力・ファイルパスは未対応）。

---

## 必要なインストール手順

### 1. Python と venv

- **Python 3.10 以上**を推奨（pyenv や venv で環境を分けるとよいです）。

```bash
cd /path/to/daily-fast-tts
python -m venv .venv
source .venv/bin/activate   # Windows の場合は .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. pyttsx3 と音声まわり

- **必須**: `pip install -r requirements.txt` で `pyttsx3` と `pyperclip` が入ります。これだけで `python -m src.main` は動作します。
- **Windows**: pyttsx3 は SAPI を使います。日本語音声を使う場合は、OS の音声パックなどで日本語ボイスを入れておいてください。
- **Linux / WSL**: 音声出力に `espeak` や `libespeak` が必要な場合があります。例:
  - Ubuntu: `sudo apt install espeak libespeak-dev`
  - 日本語を優先する場合は、日本語対応の音声パッケージを入れておくとよいです。
- **SBV2**（`--engine sbv2`）を使う場合のみ、`requests` と `pydub` が使われます（requirements.txt に含まれています）。再生には ffmpeg または simpleaudio があるとよいです。**SBV2 サーバーはまだ必須ではありません。** 後からサーバーを立て、設定で URL 等を差し替える設計です。

---

## サンプル操作手順（クリップボード読み上げ）

1. 読み上げたい文章をブラウザやエディタで**選択**する。
2. **Ctrl+C** でコピーする。
3. ターミナルでプロジェクトルートに移動し、次を実行する。
   - **通常（即再生）**:  
     `python -m src.main`
   - **WSL など**:  
     `./scripts/run_tts.sh`
4. クリップボードの内容が一定長（既定 10 文字）以上なら、その場で読み上げが始まり、終了するとプロセスも終了します。
5. クリップボードが**空**のときは「クリップボードが空です」、**短い**ときは「テキストが短すぎます（N文字）」と表示して終了します。

### コマンドラインの例

| 目的 | コマンド |
|------|----------|
| クリップボードを読み上げる | `python -m src.main` |
| pyttsx3 を明示して読み上げる | `python -m src.main --engine pyttsx3` |
| 音声をファイルに保存する | `python -m src.main --save output.wav` |
| 詳細ログを出す（デバッグ用） | `python -m src.main -v` |
| SBV2 を使う（サーバー起動済み前提） | `python -m src.main --engine sbv2` |

読み上げ速度・音量・優先する音声ID・最小文字数は **`src/config.py`** で変更できます。環境変数 `PYTTSX3_RATE`、`PYTTSX3_VOLUME`、`PYTTSX3_VOICE_ID` でも上書き可能です。

---

## プロジェクト構成

```
daily-fast-tts/
├── src/
│   ├── main.py          # エントリ: クリップボード → TTS → 再生
│   ├── config.py        # 設定（速度・音量・SBV2 の URL/パラメータ等）
│   ├── tts_base.py      # TTS エンジン共通インターフェース
│   ├── tts_pyttsx3.py   # pyttsx3 版（CPU・軽量・デフォルト）
│   └── tts_sbv2.py      # Style-Bert-VITS2 /voice API クライアント
├── scripts/
│   └── run_tts.sh       # WSL から実行するスクリプト
├── docs/
│   └── GPU_TTS_INTEGRATION_PLAN.md  # GPU 統合の計画メモ
├── README.md
└── requirements.txt
```

---

## Style-Bert-VITS2（SBV2）について

- **SBV2 サーバー構築は後で行う想定です。** 公式の `server_fastapi.py`（`/voice`）や、hideyuda 版・Zenn 等で紹介されている API サーバーに、URL とパラメータを変えるだけで接続できるようにしてあります。
- サーバーが起動していない状態で `--engine sbv2` を指定すると、「SBV2 サーバーが起動していない」旨のメッセージで終了します。
- どの GPU エンジンを本採用するかはユーザーが後で決める前提で、**枠組みと設定項目**だけ整えてあります。

### 将来 SBV2 を有効にする場合にユーザーが埋める主な設定

SBV2 サーバーを立てたあと、次のいずれかで接続先・話者・話速などを指定します（`src/config.py` の既定値か、環境変数で上書き）。

| 設定 | 説明 | ユーザーがやること |
|------|------|---------------------|
| **base_url** | API のベース URL | サーバーを起動したアドレス・ポートに合わせて設定（例: `http://127.0.0.1:5000`） |
| **speaker_id** / **speaker_name** | 話者 | サーバー側のモデル・話者一覧に合わせて指定 |
| **model_id** / **model_name** | モデル | 利用するモデルに合わせて指定 |
| **language** | 言語 | 日本語なら `JP` |
| **length**（length_scale） | 話速 | 大きいほど遅い。好みで調整（例: `1.0`〜`1.5`） |
| **style** / **style_weight** | スタイル | サーバーがサポートしていれば指定 |

上記は環境変数 `SBV2_BASE_URL`, `SBV2_SPEAKER_ID`, `SBV2_LENGTH`, `SBV2_LANGUAGE`, `SBV2_STYLE` などで上書きできます。一覧は以下を参照してください。

| 環境変数 | 説明 | 例 |
|----------|------|-----|
| `SBV2_BASE_URL` | API のベース URL | `http://127.0.0.1:5000` |
| `SBV2_ENDPOINT` | エンドポイントパス | `/voice` |
| `SBV2_TIMEOUT` | リクエストタイムアウト（秒） | `30` |
| `SBV2_MODEL_ID` | モデル ID | `0` |
| `SBV2_SPEAKER_ID` | 話者 ID | `0` |
| `SBV2_LENGTH` | 話速（大きいほど遅い） | `1.0` |
| `SBV2_LANGUAGE` | 言語 | `JP` |
| `SBV2_STYLE` | スタイル名 | `Neutral` |

その他 `SBV2_SDP_RATIO`, `SBV2_NOISE`, `SBV2_NOISEW`, `SBV2_STYLE_WEIGHT`, `SBV2_MODEL_NAME`, `SBV2_SPEAKER_NAME` なども `config.py` で定義されています。

---

## 今後の予定

- SBV2 サーバーをローカルに立て、上記環境変数で接続して高品質読み上げを利用する。
- リファクタや設定の外部ファイル化（YAML/環境変数など）は必要に応じて追加します。
