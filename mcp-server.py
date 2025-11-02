from dotenv import load_dotenv
from fastmcp import FastMCP
import json
import aiohttp
import os
import asyncio
from utils import clean_html_to_text

mcp = FastMCP("getDocs")

load_dotenv()
async def search_serper(query: str) -> dict | None:
    url = "https://google.serper.dev/search"
    
    payload = json.dumps({
        "q": query,
        "num": 3
    })
    
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers) as response:
            data = await response.json()
            return data

async def fetch_url(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.text()
            return clean_html_to_text(data)

docs_urls = {
    "langchain": "python.langchain.com/docs",
    "llama-index": "docs.llamaindex.ai/en/stable",
    "openai": "platform.openai.com/docs",
    "uv": "docs.astral.sh/uv",
}

@mcp.tool()
async def get_docs(query: str, library: str):
    """
    Search the latest docs for a given query and library.
    Supports langchain, openai, llama-index and uv.

    Args:
        query: The query to search for (e.g. "Publish a package with UV")
        library: The library to search in (e.g. "uv")

    Returns:
        Summarized text from the docs with source links.
    """
    if library not in docs_urls:
        raise ValueError(f"Library {library} not supported by this tool")
    
    query = f"site:{docs_urls[library]} {query}"

    results = await search_serper(query)
    if len(results["organic"]) == 0:
        return "No results found"

    text_parts = []
    for result in results["organic"]:
        link = result.get("link", "")        
        print(f"link: {link}")
        raw = await fetch_url(link)
        if raw:
            labeled = f"SOURCE: {link}\n{raw}"
            text_parts.append(labeled)
    return "\n\n".join(text_parts)


# async def main():
#     query = "CROMA DB"
#     library = "langchain"
#     result = await get_docs(query, library)
#     print(result)

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    # asyncio.run(main())
    main()
