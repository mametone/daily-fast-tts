# 日常高速TTS - 実装状況

> Notion「[日常高速TTS](https://www.notion.so/30b7c88ab54d800dbb6bf2a85440207c)」「Cursor」の記録とリポジトリを整理した整理メモ。  
> 優先方針: **pyttsx3 を日常利用レベルまで磨く / SBV2 等 GPU エンジンは枠組みと設定のみ整える。**

---

## 1. ファイル役割

| ファイル | 役割 |
|----------|------|
| **src/main.py** | エントリポイント。クリップボード取得 → 長さチェック → エンジン取得 → `speak(text)` または `synth_and_save(text, path)`。`--engine` / `--save` を解釈。 |
| **src/config.py** | 設定定義。pyttsx3 用: `DEFAULT_RATE`, `DEFAULT_VOLUME`, `MIN_TEXT_LENGTH`, `DEFAULT_ENGINE`。SBV2 用: `SBV2_BASE_URL`, `SBV2_ENDPOINT`, `SBV2_PARAMS` 等（環境変数で上書き可）。 |
| **src/tts_base.py** | TTS 共通インターフェース。`TextToSpeechEngine` 抽象クラスで `speak(text)` と `synth_and_save(text, path)` を定義。 |
| **src/tts_pyttsx3.py** | pyttsx3 実装。`Pyttsx3Engine` が `TextToSpeechEngine` を実装。日本語音声を名前で自動選択し、config の rate/volume を適用。 |
| **src/tts_sbv2.py** | Style-Bert-VITS2 用クライアント。`Sbv2TtsEngine` が config/環境変数の URL・パラメータで `/voice` API を叩き、WAV 取得 → 再生 or 保存。サーバー未起動時は `RuntimeError` でメッセージ表示。 |
| **scripts/run_tts.sh** | WSL 等から `python -m src.main` を実行するラッパー。`.venv` があれば自動で有効化。 |
| **docs/GPU_TTS_INTEGRATION_PLAN.md** | GPU 対応 TTS 統合の計画・ToDo（SBV2 優先、API クライアント実装済みの記録あり）。 |

---

## 2. 「任意テキスト → TTS」のエントリポイント

- **唯一の入力経路**: クリップボード（選択 → コピーしたテキスト）。
- **エントリ**:
  - `python -m src.main`  
    クリップボードのテキストを取得 → 一定長以上なら TTS で即再生。
  - `python -m src.main --save <PATH>`  
    同上だが、再生せず指定パスに WAV 保存。
  - `python -m src.main --engine pyttsx3` / `--engine sbv2`  
    使用するエンジンを明示（デフォルトは `pyttsx3`）。
- **流れ**: `pyperclip.paste()` → `strip()` → `len(text) < MIN_TEXT_LENGTH` ならメッセージ表示して終了 → `get_engine(args.engine)` → `engine.speak(text)` または `engine.synth_and_save(text, path)`。

---

## 3. いまの段階での「任意の文章を読み上げる」操作手順

1. **前提**
   - Python 3.10+、`pip install -r requirements.txt` 済み。
   - WSL/Linux の場合は音声出力に espeak 等が必要な場合あり（日本語ボイスは環境次第）。
2. **手順**
   - 読み上げたい文章を選択して **Ctrl+C** でコピー。
   - プロジェクトルートで:
     - `python -m src.main`  
       または  
     - `./scripts/run_tts.sh`（必要なら `source .venv/bin/activate` を事前に実行）。
3. **結果**
   - クリップボードが空、または `MIN_TEXT_LENGTH`（既定 10）未満 → エラーメッセージを stderr に表示して終了。
   - それ以外 → デフォルトでは pyttsx3 で即再生し、再生終了後にプロセス終了。

---

## 4. できていること / まだできていないこと

### いまの時点でできていること

- クリップボード入力による「任意テキスト → TTS 即再生」（pyttsx3）。
- オプションで WAV 保存（`--save`）。
- エンジン切り替えの受け口（`--engine pyttsx3` / `--engine sbv2`）。
- 短文・空クリップボード時の「短すぎます」メッセージと即終了。
- 設定で読み上げ速度（rate）・音量（volume）・最小文字数を変更可能（config.py）。
- pyttsx3 で日本語を優先する音声の自動選択（名前で Japanese / Mei 等を検出）。
- SBV2 用クライアント実装（config/環境変数で URL・パラメータ差し替え可能）。サーバー未起動時はメッセージ付きで終了。
- 完全ローカル・完全無料（pyttsx3 は OS 標準エンジン利用、クラウド API なし）。

### 整備済み（ステップ2で対応）

- **設定**: `config.py` および環境変数で rate（`PYTTSX3_RATE`）/ volume（`PYTTSX3_VOLUME`）/ 優先音声ID（`PYTTSX3_VOICE_ID`）を変更可能。
- **挙動**: クリップボードが空のとき「クリップボードが空です」、短いとき「テキストが短すぎます（N文字）」と分けて表示して終了。
- **堅牢性**: TTS 実行時の例外をキャッチし、`logging` でログ出力して stderr にメッセージを出して exit 1。
- **CLI**: `python -m src.main`（クリップボード読み上げ）、`--engine pyttsx3` / `--engine sbv2`、`--save PATH`、`-v`（詳細ログ）。

### まだできていないこと

- **ドキュメント**: README の「現時点でできること」「インストール手順」「サンプル操作手順」の明文化と、SBV2 を有効にする際にユーザーが埋める設定値の説明（ステップ2・3で整備予定）。
- **SBV2**: サーバーは未セットアップ想定。利用する場合はユーザーがサーバーを立て、config/環境変数を埋める必要あり。

---

## 5. 方針の確認

- **現時点**: pyttsx3 一本で日常利用レベルまで磨き、SBV2 等 GPU エンジンは「後でユーザーが選ぶ前提の枠組み・設定項目」のみ整える。
- **入力**: 当面はクリップボード専用（標準入力・ファイルパスは希望なし）。
- **課金・クラウド**: 使用しない（完全無料・ローカル前提）。
