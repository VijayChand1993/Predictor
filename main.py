from fastapi import FastAPI

from api.routes import items, health, chart, dasha, transit, aspect

app = FastAPI(
    title="Vedic Astrology Scoring Engine",
    description="A comprehensive Vedic astrology scoring engine with natal chart generation and analysis",
    version="1.0.0"
)

# Include routers
app.include_router(health.router)
app.include_router(items.router)
app.include_router(chart.router)
app.include_router(dasha.router)
app.include_router(transit.router)
app.include_router(aspect.router)


@app.get("/")
async def root():
    """Root endpoint returning a welcome message."""
    return {
        "message": "Welcome to the Vedic Astrology Scoring Engine!",
        "docs": "/docs",
        "health": "/health",
        "chart_api": "/chart",
        "dasha_api": "/dasha",
        "transit_api": "/transit",
        "aspect_api": "/aspect"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

