from fastapi import FastAPI

from agentdex import __version__

app = FastAPI(
    title="agentdex",
    version=__version__,
    description="VEX playground — hub-and-leaf swarm on ai-builders-coach MCP",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "agentdex",
        "lane": "showcase-dogfood",
        "trio": "ionq · helios · oppie",
    }
