from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from rich import print
import os
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key = os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str)-> str:
    """ Search the web for recent information on a topic. Returns Titles , URLs and snippets.    """
    results = tavily.search(query=query , max_results= 3  )
    out = []
    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:200]}\n"
        )
    return "\n-----\n".join(out)

@tool
def scrape_url(url : str)-> str:        
    """ Scrape the content of a webpage. Returns the text content of the page. """
    try:
        response = requests.get(url , timeout=10 , headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
            tag.decompose() 
        return soup.get_text(separator= " ", strip = True)[:2000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"