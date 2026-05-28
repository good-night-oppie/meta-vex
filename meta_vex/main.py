from fastapi import FastAPI

from meta_vex import __version__

app = FastAPI(
    title="meta-vex",
    version=__version__,
    description="VEX playground — hub-and-leaf swarm on ai-builders-coach MCP",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "meta-vex",
        "lane": "showcase-dogfood",
        "trio": "ionq · helios · oppie",
    }
