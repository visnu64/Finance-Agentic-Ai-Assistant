import openai
from phi.agent import Agent
import phi.api
from phi.model.openai import OpenAIChat
from phi.tools.yfinance import YFinanceTools
from phi.tools.duckduckgo import DuckDuckGo
from dotenv import load_dotenv
import os
import phi
from phi.playground import playground, serve_playground_app
from fastapi import FastAPI


load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

phi.api = os.getenv('PHI_API_KEY')

web_search_agent = Agent(
    name='web search agent',
    role='search the web for information',
    model=OpenAIChat(id='openai/gpt-oss-120b:free',base_url="https://openrouter.ai/api/v1"),
    tools=[DuckDuckGo()],
    instructions=['Always include sources'],
    show_tool_calls = True,
    markdown =True,
)

finance_agent = Agent(
    name="finance AI agent",
    model = OpenAIChat(id='openai/gpt-oss-120b:free',base_url="https://openrouter.ai/api/v1"),
    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            company_info= True,
            company_news= True,
            key_financial_ratios= True,
        )
    ],
    instrutions=['use tables to display data'],
    show_tool_calls= True,
    markdown =True,
)

app = playground(agents=[finance_agent, web_search_agent]).get_app()

if __name__ == "__main__":
    serve_playground_app('playground:app', reload=True)