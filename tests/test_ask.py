"""app/ask.py のテスト（APIキー・通信なし。genai.Client を差し替える）。"""

from types import SimpleNamespace

from app import ask as ask_mod


class FakeChat:
    def __init__(self):
        self.history = []

    def send_message(self, q):
        self.history += [q, f"answer to {q}"]
        return SimpleNamespace(
            text=f"answer({len(self.history) // 2})",
            usage_metadata=SimpleNamespace(prompt_token_count=len(self.history), candidates_token_count=3, total_token_count=len(self.history) + 3),
        )

    def get_history(self):
        return self.history


class FakeClient:
    def __init__(self, api_key=None):
        self.chats = SimpleNamespace(create=lambda model, config=None: FakeChat())
        self.models = SimpleNamespace(
            generate_content=lambda model, contents, config=None: SimpleNamespace(
                text="ok", usage_metadata=SimpleNamespace(prompt_token_count=5, candidates_token_count=2, total_token_count=7)
            )
        )


def _patch(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy")
    monkeypatch.setattr(ask_mod.genai, "Client", FakeClient)


def test_ask_prints_tokens(monkeypatch, capsys):
    _patch(monkeypatch)
    assert ask_mod.ask("hi", temperature=0.5) == "ok"
    assert "入力: 5 / 出力: 2" in capsys.readouterr().out


def test_chat_keeps_history(monkeypatch, capsys):
    _patch(monkeypatch)
    inputs = iter(["2問目", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    ask_mod.chat_loop(first="1問目")
    out = capsys.readouterr().out
    assert "answer(1)" in out and "answer(2)" in out
    assert "[履歴] 4 件" in out
