"""第3回 宿題・発展(a): 演習のエージェントを Google ADK で組み立て直したもの。

指示（INSTRUCTIONS）とツールは Pydantic AI 版とまったく同じものを使い、
エージェントを組み立てる部分だけを ADK に置き換えている。
"""

from google.adk.agents import Agent

from app import tools
from app.agent import INSTRUCTIONS

root_agent = Agent(
    model="gemini-3.5-flash-lite",
    name="glossary_agent",
    instruction=INSTRUCTIONS,
    tools=[tools.search_glossary, tools.get_lecture_summary, tools.make_quiz],
)
