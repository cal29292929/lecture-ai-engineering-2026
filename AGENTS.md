# AIE2026 演習・宿題リポジトリ（作業メモ）

## プロジェクト概要
松尾・岩澤研「AIエンジニアリング実践講座（AIE2026）」の演習・宿題用リポジトリ（講座 repo の fork で作業）。
講座を通して、学習支援エージェントを少しずつ育てる。各回 `lectures/NN/problem.md` が課題、`lectures/NN/answer.md` が提出物。

## セットアップ
- Python 3.12 + uv。`uv sync --frozen`（依存の版は固定。上げない）
- 環境変数 `GEMINI_API_KEY`（コード・コミット・ログに書かない）。モデルは `AIE_MODEL` で切替（既定 gemini-3.5-flash-lite）

## 実行
- テスト（APIキー不要）: `uv run pytest -q`
- 1回質問: `uv run python -m app.ask "LoRAとは何ですか？" [--temperature 0.7]`
- 会話モード（第1回 宿題・実装）: `uv run python -m app.ask --chat`

## 提出の流れ
回ごとにブランチ（例 `lec01`）→ answer.md 記入 → commit/push → **自分の fork 内で** ブランチ→main の PR。
出席アンケート・宿題は講座の学習管理システムから、**次週月曜 17:00 締切**（修了要件）。

## 第1回の課題と状況（ブランチ `lec01`）
- 演習: token 数表示（app/ask.py の TODO）→ 実装済み
- 宿題（1つでよい）: 基礎=モデル/temperature を変えて3回ずつ比較、実装=会話履歴つき質問、発展=応答時間・トークン数比較
  - **実装レベルを選択**し `--chat` を実装済み、`tests/test_ask.py` 追加、全テスト通過
- 未完了: APIキーで実際に動かし、answer.md の「要実行/要記入」欄を自分の結果で埋める → push → PR → 学習管理システムで提出

## 次のステップ
1. APIキーを環境変数で設定し `uv run python -m app.ask` と `--chat` を実行
2. answer.md を結果で更新（うまくいかなかった結果もそのまま書く）
3. `git push -u origin lec01` → fork 内で PR（base が自分の fork であることを確認）

## ルール
- APIキーを answer.md・コード・ログ・スクショに書かない
- 講義資料・宿題の内容を外部（SNS等）に出さない
- 個人情報をファイルに書かない
