# 第1回 解答

## 演習

- 講座に固有の質問（宿題の3レベル）へのモデルの回答（要約でよい）：（要実行：GEMINI_API_KEY 設定後に `uv run python -m app.ask` の結果を記入）
- 用語集の正しい意味と比べて気づいたこと：（要記入。正解は data/glossary.json の homework-levels）
- 表示できたトークン数（入力 / 出力）：（要実行：`[tokens] 入力: … / 出力: …` の値を記入）

## 宿題

- 取り組んだレベル：実装
- やったこと：
  - `app/ask.py` に `--chat` オプションを追加し、`client.chats.create()` のチャットセッションで会話履歴を保ったまま続けて質問できるようにした（空行・exit・quit で終了）
  - 各応答のあとに入力/出力トークン数と履歴件数を表示
  - `--temperature` オプションを追加（`GenerateContentConfig(temperature=...)`）
  - `tests/test_ask.py` を追加（APIキーなしで、履歴が保たれることを確認）
- 使ったモデル：gemini-3.5-flash-lite（既定）
- 結果：（要実行：`uv run python -m app.ask --chat` で「LoRAとは？」→「それをColabで試すには？」のように前の質問を指す質問をして、文脈が引き継がれるかを記入）
- 気づき・疑問：（要記入。例：履歴が増えるほど入力トークン数が増える＝無料枠を早く消費する）
