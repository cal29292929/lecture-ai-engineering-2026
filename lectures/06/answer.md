# 第6回 解答

## 演習

- `--list-tools` で見えたツール名と、第3回（`--mcp` なし）との違い：直接登録（第3回方式）は `search_glossary` と `get_lecture_summary` の2つ。MCP 経由は当初 `glossary_search_glossary` の1つだけで、ツール名にサーバー名の接頭辞「glossary_」が付く。説明文と引数は tools.py の docstring と型ヒントそのもので、モデルから見た形は直接登録と同じだった
- `--mcp --trace` で見えたツール呼び出し（ツール名と引数）と、`requests` の回数：「AIE2026の講座の宿題にある「3レベル」とは何ですか？」で、直接登録は `search_glossary({'query': '3レベル'})`、MCP は `glossary_search_glossary({'query': '3レベル'})` が呼ばれ、どちらも requests は2回。入力トークンは直接登録 783 に対し MCP は 1,081 で、MCP の方がツールの説明などの分だけ増えた
- MCP サーバーに公開したツールと、その説明文：`get_lecture_summary`（「指定した回（1始まりの整数）の講義の要点を返す」）。`--mcp --list-tools` に `glossary_get_lecture_summary` が増え、`--mcp --trace "第2回では何を学びますか？"` で `glossary_get_lecture_summary({'lecture': 2})` が呼ばれて第2回の要点が返ることを確認した
- fetch サーバーを足したときのツール呼び出し（ツール名と引数）：`app/mcp_servers.json` に fetch を足すとツールが4つになり `fetch_fetch` が増えた。`--mcp --trace "https://modelcontextprotocol.io/ の冒頭を日本語で3行に要約して"` では `fetch_fetch({'url': 'https://modelcontextprotocol.io/'})` が呼ばれた。ただしこの実行環境では外部サイトへの直接接続ができず、robots.txt の取得で失敗したため、ページ内容の取得まではできなかった（モデルはネットワークエラーであることをそのまま伝えた）

## 宿題

- 取り組んだレベル：基礎・実装・発展

### 基礎

- やったこと：`app/mcp_server.py` に `server.tool()(tools.get_lecture_summary)` の1行を足し、`search_glossary` と同じ書き方で `get_lecture_summary` を MCP サーバーに公開した。エージェント側（`app/agent.py` と設定ファイルの glossary の項目）は変更していない
- 結果：`--mcp --list-tools` に `glossary_get_lecture_summary` が増え、`--mcp --trace "第2回では何を学びますか？"` で実際に呼ばれた。`uv run pytest -q` は全19件パスした

### 実装

- やったこと：第3回で作った `make_quiz` を `app/tools.py` に取り込み、`app/mcp_server.py` で `server.tool()(tools.make_quiz)` として MCP に公開した。引数の範囲チェックとして、その回の用語が用語集に無い場合は例外にせず「第○回の用語は用語集にありません。別の回を指定してください。」というメッセージを文字列で返すようにした（第3回の実装と同じ形）。`tests/test_mcp_server.py` に TestModel を使ったテストを追加した（`glossary_make_quiz` が公開されていること、MCP 越しに呼ばれて結果が戻ること、`make_quiz(2)` が問題と答えの JSON を返すこと、`make_quiz(99)` がメッセージを返すこと）
- 結果：`--mcp --trace "第99回の確認問題を1問出して"` で `glossary_make_quiz({'lecture': 99})` が呼ばれ、範囲チェックのメッセージがツールの戻り値としてモデルに渡った。モデルはそれを読み、「第99回は範囲外のようです。別の回を指定してください」と利用者に伝えた。例外ではなく通常の戻り値なので、モデルにはエラーではなく情報として見え、会話の中で処理された。テストは追加分も含めて全19件パスした
- 気づき・疑問：「第99回のクイズを作って」と聞いたときは、モデルが先に `glossary_get_lecture_summary({'lecture': 99})` を選び、そちらの「要点はまだありません」という結果から同じ結論を答えた。どちらのツールで範囲外に気づくかは質問の言い方で変わる。範囲チェックを「例外で落とす」か「メッセージを返す」かで、モデルに見える形と、その後の振る舞いが変わるのが面白かった

### 発展

- やったこと：自分が使っている Claude Code について、MCP サーバーの設定方法を公式ドキュメントで調べ、演習の `app/mcp_servers.json` と比べた（調査日：2026-11-25、参照：https://code.claude.com/docs/en/mcp ）
- 結果：
  - 設定のスコープは3つある。local（既定）は `~/.claude.json` にプロジェクトパス配下で保存され、そのプロジェクトでのみ有効で非公開。project はプロジェクトルートの `.mcp.json`（`mcpServers` キー）に保存され、チームで共有でき、使う前に承認プロンプトが出る。user は `~/.claude.json` に保存され、全プロジェクトで有効。追加は `claude mcp add` や `claude mcp add-json` のコマンドでもできる
  - コマンドで起動する書き方（stdio）は `claude mcp add <名前> -- <コマンド> [引数...]` で、JSON では `{"command": ..., "args": [...], "env": {...}}` と書き、`type` が無ければ stdio と解釈される
  - URL で接続する書き方は `claude mcp add --transport http <名前> <URL>` で、JSON では `"type": "http"`（または sse / ws）と `"url"` の両方が必須。url だけだと設定エラーになる
  - 演習の `app/mcp_servers.json` との違い：トップレベルの `mcpServers` と stdio の command / args の形式はほぼ共通で、project スコープの `.mcp.json` に近い。一方、演習側は `app/agent.py` が読む単一ファイルで、スコープや承認の概念がなく、URL 接続も `{"url": ...}` だけで type を書かない。Claude Code 側は、スコープによる保存先の分離、CLI による管理、トランスポートの明示、プロジェクトサーバーの承認フロー、環境変数展開や OAuth まで備えている点が大きく違う
- 気づき・疑問：演習の設定ファイルがそのまま実用ツールの project スコープの形に近いのは、MCP の設定形式が共通化されているおかげだと分かった。実務では「どのスコープに置くか」「承認を挟むか」が安全性を決めるので、サーバーを足すときは出所と置き場所を選ぶことが大事だと思った
