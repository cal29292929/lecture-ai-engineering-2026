"""第1回: 素のLLMに1回だけ質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

ツールも会話履歴も持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors, types

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def _config(temperature: float | None) -> types.GenerateContentConfig | None:
    if temperature is None:
        return None
    return types.GenerateContentConfig(temperature=temperature)


def print_usage(response) -> None:
    """第1回 演習: 入力トークン数と出力トークン数を表示する。"""
    usage = response.usage_metadata
    if usage is None:
        print("[tokens] 取得できませんでした")
        return
    print(
        f"[tokens] 入力: {usage.prompt_token_count} / 出力: {usage.candidates_token_count}"
        f" / 合計: {usage.total_token_count}"
    )


def ask(question: str, temperature: float | None = None) -> str:
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(
        model=MODEL, contents=question, config=_config(temperature)
    )
    print_usage(response)
    return response.text


def chat_loop(temperature: float | None = None, first: str | None = None) -> None:
    """第1回 宿題（実装）: 会話履歴を保ったまま続けて質問する。

    client.chats はこれまでのやり取りを履歴として毎回モデルに渡す。
    空行・exit・quit で終了する。
    """
    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL, config=_config(temperature))
    question = first
    while True:
        if question is None:
            try:
                question = input("あなた> ").strip()
            except EOFError:
                break
        if question in ("", "exit", "quit"):
            break
        try:
            response = chat.send_message(question)
        except errors.APIError as e:
            print(api_error_message(e.code, e.message))
        else:
            print(f"AI> {response.text}")
            print_usage(response)
            print(f"[履歴] {len(chat.get_history())} 件\n")
        question = None


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=None)
    parser.add_argument("--chat", action="store_true", help="会話履歴を保って続けて質問する")
    parser.add_argument("--temperature", type=float, default=None, help="例: 0.0〜2.0")
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    if args.chat:
        chat_loop(args.temperature, args.question)
        return
    if args.question is None:
        args.question = DEFAULT_QUESTION

    print(f"[model] {MODEL}")
    print(f"[質問] {args.question}\n")
    try:
        print(ask(args.question, args.temperature))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
