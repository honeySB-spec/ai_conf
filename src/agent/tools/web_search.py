from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

@tool("duckduckgo_search")
def web_search(search_query: str):
    """Search the web for information about past events and ticket prices."""
    return search_tool.run(search_query)
