# GPU対応TTSエンジン統合計画

> Notion「日常高速TTS」「開発環境」の内容を踏まえた分析・提案。  
> 設計メモ: [日常高速TTS](https://www.notion.so/30b7c88ab54d800dbb6bf2a85440207c)、[開発環境](https://www.notion.so/30b7c88ab54d809c9271da849cc5b810)

---

## 1. 開発環境の前提整理

| 項目 | 内容 |
|------|------|
| **OS** | WSL2 / Ubuntu 24.04 |
| **CPU** | Intel Core i7-13700F |
| **メモリ** | 64GB |
| **GPU** | NVIDIA RTX 4070 Ti（**VRAM 12GB**） |
| **CUDA** | 12.1 |
| **Python** | 3.12 推奨 |
| **PyTorch** | cu121（2.0+、例: 2.5.1） |
| **FlashAttention 2** | RTX 4070 Ti 対応、VRAM節約・高速化に有効 |

**TTSエンジン選定の観点**:
- 12GB VRAM は中〜大型モデルまで対応可能
- CUDA 12.1 に合わせた `cu121` の PyTorch が必要
- 「日常利用での高速読み上げ」のため、**推論速度**・**起動の軽さ**・**セットアップの簡単さ**を重視

---

## 2. TTSエンジン候補の評価

### 2.1 候補一覧と評価

| エンジン | 推論速度 | 起動の軽さ | セットアップ | 日本語品質 | VRAM目安 | 備考 |
|----------|----------|------------|--------------|------------|----------|------|
| **Style-Bert-VITS2** | ◎ 高速 | △ API常駐 or 都度ロード | ○ 手順明瞭 | ◎ 高い | 2〜4GB | WebUI/API、モデルDL必要 |
| **ESPnet2** | ◎ RTF&lt;0.1 | △ モデルロード必要 | ○ pip 中心 | ○ プリモデル | 1〜2GB | 日本語プリトレイン豊富 |
| **Qwen3-TTS** | ○ | △ 1.7B で約5GB | △ 依存多め | ◎ 高品質 | 約4〜5GB | 開発環境で既に利用実績あり |
| **Coqui XTTS-v2** | ○ 低遅延 | △ | ○ pip | ◎ クローン可 | 2〜3GB | 多言語、クローン音声 |

### 2.2 日常TTS用途での推奨優先順位

1. **Style-Bert-VITS2**（最優先）
   - 日本語特化で自然さ◎、API で即応、Notion の比較表で最も推奨
   - サーバーを常駐させる運用なら「起動の軽さ」をクリア
   - VRAM 2〜4GB 程度で 12GB に余裕あり

2. **ESPnet2**
   - RTF が低く推論は高速、pip 中心で導入しやすい
   - 日本語プリトレインモデルが豊富
   - ライブラリ依存が比較的シンプル

3. **Qwen3-TTS**
   - 開発環境の Voice-clone プロジェクトで実績あり
   - 品質は高いが、モデル・依存が重く「日常の高速読み上げ」にはややオーバースペック
   - 将来のオプションとしては有力

**結論**: まず **Style-Bert-VITS2** を統合し、必要に応じて ESPnet2 や Qwen3-TTS を追加する方針とする。

---

## 3. 現在のコードレビュー

### 3.1 入出力フロー

```
[クリップボード] --pyperclip.paste()--> [main.py]
                                              |
                                              v
                                    text.strip(), 長さチェック
                                              |
                                              v
                                    get_engine(engine_name)
                                              |
                        +-------------------+-------------------+
                        v                                         v
              [Pyttsx3Engine]                           [StyleBertVITS2Engine]
                  speak(text)                                    (未実装)
               or synth_and_save(text, path)
                        |
                        v
              [即時再生 or WAV保存]
```

### 3.2 問題点・改善点

| 項目 | 現状 | 改善案 |
|------|------|--------|
| エンジン切り替え | `--engine pyttsx3|sbv2` で指定可能 | 設定ファイル（YAML/JSON）や環境変数での指定も対応 |
| SBV2 実装 | スケルトンのみ | API 版（サーバー常駐）とローカル推論版の両対応を検討 |
| エンジン取得 | `main.py` 内で直書き | ファクトリやレジストリ化して拡張しやすくする |
| 再生方式 | pyttsx3 は `runAndWait` で同期的 | GPU 版は WAV 生成 → pydub/simpleaudio で再生の流れに統一 |
| ログ・計測 | なし | 推論時間・VRAM 使用量をオプションでログ出力 |

### 3.3 GPU エンジン差し替えのしやすさ

- **`TextToSpeechEngine`** の `speak()` / `synth_and_save()` が共通インターフェースとして適切
- GPU 版は「テキスト → WAV バイト列 → 再生 or 保存」の流れにすれば、既存の main のフローと整合する
- 将来的に `synth_to_bytes(text) -> bytes` を追加し、再生・保存の両方で再利用する設計も検討価値あり

---

## 4. Style-Bert-VITS2 統合の詳細

### 4.1 運用パターン

- **パターンA: API サーバー常駐**  
  別プロセスで `server_editor.py` などを起動し、`tts_sbv2.py` から HTTP API を叩く。
- **パターンB: ローカル推論**  
  本プロセス内で SBV2 をロードし、`speak()` 呼び出し時に直接推論。

日常利用では **パターンA** を推奨（都度モデルロードが不要で起動が軽い）。

### 4.2 インストール・セットアップ概要

- **API 利用時**: SBV2 は別リポジトリでセットアップ。本プロジェクト側は `requests`, `pydub` を追加
- **ローカル推論時**: SBV2 を submodule または pip で導入し、PyTorch cu121 と整合させる

### 4.3 推論速度の目安

- 日本語 100 文字あたり、GPU で数秒程度（環境・モデルに依存）
- VoiceVox より速く、「即時再生」の体感には十分な想定

---

## 5. 具体的な ToDo リスト

### Phase 1: 基盤整備（差し替えしやすい設計）

| # | タスク | 対象ファイル | 内容 |
|---|--------|--------------|------|
| 1.1 | エンジンファクトリの整理 | `src/engine_factory.py`（新規） | `get_engine(name) -> TextToSpeechEngine` を移動し、main.py を簡素化 |
| 1.2 | 設定の拡張 | `src/config.py` | エンジン名・SBV2 API URL 等を環境変数で上書き可能にする |
| 1.3 | `synth_to_bytes` の追加（オプション） | `src/tts_base.py` | 再生・保存の共通化のため、デフォルト実装で `synth_and_save` を利用 |

### Phase 2: Style-Bert-VITS2 統合

| # | タスク | 対象ファイル | 内容 |
|---|--------|--------------|------|
| 2.1 | SBV2 API クライアント実装 | `src/tts_sbv2.py` | `/tts_fn` 等の API を叩き、WAV バイト列を取得 |
| 2.2 | 即時再生の実装 | `src/tts_sbv2.py` | WAV バイト列 → pydub → 再生。`pydub`, `simpleaudio` 等を追加 |
| 2.3 | 保存機能の実装 | `src/tts_sbv2.py` | レスポンスをそのまま path に保存 |
| 2.4 | requirements の更新 | `requirements.txt` | `requests`, `pydub` 追加。GPU 版用は `requirements-gpu.txt` を別途検討 |
| 2.5 | SBV2 セットアップ手順 | `docs/SETUP_SBV2.md`（新規） | サーバー起動方法、モデル DL、環境変数（API URL 等） |

### Phase 3: 運用・ドキュメント

| # | タスク | 対象ファイル | 内容 |
|---|--------|--------------|------|
| 3.1 | README の更新 | `README.md` | GPU 対応版の概要、前提環境、実行方法、Notion との対応 |
| 3.2 | ログ・計測（オプション） | `src/tts_sbv2.py` | 推論時間・API レスポンス時間をログ出力するオプション |

---

## 6. 最初に着手すべき 1〜2 タスク

### 推奨: タスク 2.1 と 2.2（SBV2 の API 実装と即時再生）

- 現状の `TextToSpeechEngine` のまま、`StyleBertVITS2Engine` を**API クライアントとして完成**させる
- `speak()`: API で合成 → WAV バイト列 → pydub で即再生
- `synth_and_save()`: API で合成 → 指定 path に保存

これにより:

1. 既存の `main.py` のフローを壊さず、`--engine sbv2` で動作する
2. SBV2 サーバーを別途起動しておくだけで、すぐに高品質読み上げを試せる
3. ファクトリ整理や設定拡張は、SBV2 が動いた後にリファクタとして実施できる

### 実装済み（2025-02 時点）

- **Sbv2TtsEngine** を `src/tts_sbv2.py` に実装済み。公式 `server_fastapi.py` の **GET/POST /voice** を想定。
- base_url・エンドポイント・パラメータは `src/config.py` および環境変数（`SBV2_BASE_URL`, `SBV2_ENDPOINT`, `SBV2_MODEL_ID` 等）で切り替え可能。
- サーバー未起動時は `RuntimeError` で「SBV2 サーバーが起動していない」旨を表示。README に「現時点では pyttsx3 のみ必須」「SBV2 構築は後で行う」と明記済み。
