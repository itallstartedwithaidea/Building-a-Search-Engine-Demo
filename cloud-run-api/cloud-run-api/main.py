import os, json, httpx, uvicorn, traceback
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY    = os.getenv("SERPAPI_KEY", "")

client = OpenAI(api_key=OPENAI_API_KEY)
app    = FastAPI()


class QueryIn(BaseModel):
    query: str
    k: int = 10


async def search_with_serpapi(query: str, k: int = 10) -> list[dict]:
    async with httpx.AsyncClient() as hc:
        rsp = await hc.get(
            "https://serpapi.com/search",
            params={"engine": "google", "q": query, "api_key": SERPAPI_KEY, "num": k},
        )
    if rsp.status_code != 200:
        raise RuntimeError(f"SerpAPI HTTP {rsp.status_code}")
    return [
        {
            "title": r.get("title", "No title"),
            "snippet": r.get("snippet", "No snippet"),
            "url": r.get("link", ""),
            "thumbnail": r.get("thumbnail", ""),
        }
        for r in rsp.json().get("organic_results", [])[:k]
    ]


async def search_with_openai(query: str, k: int = 10) -> list[dict]:
    try:
        rsp = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a web-search assistant. Respond ONLY in valid JSON "
                        "with key 'results' (list of objects with title, snippet, url, thumbnail)."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Generate {k} realistic web-search results for: {query}",
                },
            ],
        )
        data = json.loads(rsp.choices[0].message.content)["results"][:k]
    except Exception:
        print("OpenAI fallback error:", traceback.format_exc())
        data = []
    while len(data) < k:
        data.append(
            {
                "title": "Not enough results",
                "snippet": "Fallback placeholder",
                "url": "https://example.com",
                "thumbnail": "",
            }
        )
    return data


@app.post("/v1/query")
async def query(inp: QueryIn):
    if SERPAPI_KEY:
        try:
            return {"results": await search_with_serpapi(inp.query, inp.k)}
        except Exception as e:
            print("SerpAPI error:", e)
    return {"results": await search_with_openai(inp.query, inp.k)}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "search_provider": "SerpAPI" if SERPAPI_KEY else "OpenAI",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
