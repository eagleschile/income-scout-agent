"""Scan Fetch.ai Agentverse marketplace for income opportunities."""
import asyncio, json
from uagents import Agent

AGENT_SEED = "PUT_YOUR_WALLET_SEED_HERE"

async def scan_marketplace():
    a = Agent(name="scout", seed=AGENT_SEED)
    
    queries = [
        "I need a web scraper for collecting product data",
        "Need data annotation service for images",
        "Looking for content moderation task worker",
        "Need PDF processing and text extraction",
    ]
    
    results = []
    for q in queries:
        results.append({
            "query": q,
            "status": "Use web_extract on https://agentverse.ai/marketplace",
        })
    
    return json.dumps(results, indent=2)

if __name__ == "__main__":
    print(asyncio.run(scan_marketplace()))