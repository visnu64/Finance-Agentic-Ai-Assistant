import streamlit as st
import openai
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.yfinance import YFinanceTools
from phi.tools.duckduckgo import DuckDuckGo
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Agentic AI", page_icon="🤖")
st.title("🤖 Visnu's finance Agentic AI Assistant")
st.caption("Automatically uses Web Search or Finance tools based on your question")

# Model 
MODEL = OpenAIChat(
    id="openai/gpt-oss-120b:free",
    base_url="https://openrouter.ai/api/v1",
)

#  Sub-agents 
@st.cache_resource
def get_orchestrator():
    web_search_agent = Agent(
        name="Web Search Agent",
        role="Search the web for news, current events, and general information",
        model=MODEL,
        tools=[DuckDuckGo()],
        instructions=["Always include sources"],
        show_tool_calls=True,
        markdown=True,
    )

    finance_agent = Agent(
        name="Finance Agent",
        role="Get stock prices, financial ratios, analyst recommendations, and company news",
        model=MODEL,
        tools=[
            YFinanceTools(
                stock_price=True,
                analyst_recommendations=True,
                company_info=True,
                company_news=True,
                key_financial_ratios=True,
            )
        ],
        instructions=["Use tables to display data"],
        show_tool_calls=True,
        markdown=True,
    )

    # Orchestrator automatically picks the right agent(s) based on the query
    orchestrator = Agent(
        name="Orchestrator",
        team=[web_search_agent, finance_agent],   
        model=MODEL,
        instructions=[
            # Fix 2: task decomposition — break complex queries into subtasks
            "Analyse the user query and break it into subtasks if needed.",
            "For web/news/general queries → delegate to Web Search Agent.",
            "For stocks/finance/company data → delegate to Finance Agent.",
            "For complex queries that need both (e.g. 'AAPL stock and latest Apple news') → "
            "delegate each part to the right agent simultaneously, then combine the results.",
            "Always produce one clear, combined final response.",
            "Use tables for financial data and always cite sources for web results.",
        ],
        show_tool_calls=True,
        markdown=True,
    )

    return orchestrator

orchestrator = get_orchestrator()

#  Chat history 
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

#  Input & response 
if user_input := st.chat_input("Ask anything — stocks, news, or both at once..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            for chunk in orchestrator.run(user_input, stream=True):
                if chunk.content:
                    full_response += chunk.content
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)

        except Exception as e:
            placeholder.error(f"⚠️ Error: {e}")
            full_response = str(e)

    st.session_state.messages.append({"role": "assistant", "content": full_response})