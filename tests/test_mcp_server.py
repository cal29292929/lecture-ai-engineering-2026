"""第6回: MCP サーバーとクライアントの配線テスト（LLM も API キーも使わない）。

app/mcp_servers.json の glossary サーバーを実際に起動し（stdio）、TestModel で
「ツールが MCP 経由で公開され、呼ばれ、結果が戻るか」を確かめる。
"""

import json

from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.test import TestModel

from app.agent import MCP_CONFIG, build_mcp_agent

GLOSSARY_TOOL = "glossary_search_glossary"  # 設定ファイルのサーバー名 "glossary" が前に付く
SUMMARY_TOOL = "glossary_get_lecture_summary"
QUIZ_TOOL = "glossary_make_quiz"


def _glossary_only_config(tmp_path):
    """設定のうち glossary サーバーだけを使う（演習で足した fetch などの外部サーバーは起動しない）。"""
    config = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    assert "glossary" in config["mcpServers"], "app/mcp_servers.json に glossary サーバーが必要"
    path = tmp_path / "mcp_servers.json"
    path.write_text(
        json.dumps({"mcpServers": {"glossary": config["mcpServers"]["glossary"]}}), encoding="utf-8"
    )
    return path


def _parts(result, kind):
    return [p for m in result.all_messages() for p in m.parts if isinstance(p, kind)]


def test_glossary_server_exposes_search_tool(tmp_path):
    model = TestModel(call_tools=[])
    build_mcp_agent(_glossary_only_config(tmp_path)).run_sync("ツール一覧", model=model)

    offered = {t.name for t in model.last_model_request_parameters.function_tools}
    assert GLOSSARY_TOOL in offered  # 演習でツールを足しても壊れないよう「含む」で判定


def test_glossary_result_comes_back_through_mcp(tmp_path):
    model = TestModel(call_tools=[GLOSSARY_TOOL])
    result = build_mcp_agent(_glossary_only_config(tmp_path)).run_sync("LoRAとは？", model=model)

    assert [p.tool_name for p in _parts(result, ToolCallPart)] == [GLOSSARY_TOOL]
    returns = _parts(result, ToolReturnPart)
    assert returns and returns[0].tool_name == GLOSSARY_TOOL
    assert str(returns[0].content).strip()  # 検索結果（または「見つかりませんでした」）が戻っている
    assert result.output


# ------------------------------------------------ 第6回 宿題（実装）: make_quiz の公開と範囲チェック
def test_glossary_server_exposes_summary_and_quiz_tools(tmp_path):
    model = TestModel(call_tools=[])
    build_mcp_agent(_glossary_only_config(tmp_path)).run_sync("ツール一覧", model=model)

    offered = {t.name for t in model.last_model_request_parameters.function_tools}
    assert SUMMARY_TOOL in offered  # 演習で公開した get_lecture_summary
    assert QUIZ_TOOL in offered  # 宿題（実装）で公開した make_quiz


def test_make_quiz_comes_back_through_mcp(tmp_path):
    # TestModel は int の引数にダミー値（0）を入れる。第0回は存在しないので、
    # 範囲チェックのメッセージが MCP 越しにそのまま戻ることもあわせて確かめる
    model = TestModel(call_tools=[QUIZ_TOOL])
    result = build_mcp_agent(_glossary_only_config(tmp_path)).run_sync("確認問題を出して", model=model)

    assert [p.tool_name for p in _parts(result, ToolCallPart)] == [QUIZ_TOOL]
    returns = _parts(result, ToolReturnPart)
    assert returns and returns[0].tool_name == QUIZ_TOOL
    assert str(returns[0].content).strip()
    assert result.output


def test_make_quiz_returns_question_and_answer():
    from app import tools

    payload = json.loads(tools.make_quiz(2))
    assert payload["question"].endswith("の意味は？")
    assert payload["answer"]  # 答え（用語の定義）が入っている


def test_make_quiz_out_of_range_returns_friendly_message():
    from app import tools

    message = tools.make_quiz(99)
    assert "第99回の用語は用語集にありません" in message
    assert "別の回を指定してください" in message
