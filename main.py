from fastapi import FastAPI

from api.routes import items, health

app = FastAPI(
    title="Sample FastAPI Application",
    description="A well-structured FastAPI application with routes and services",
    version="1.0.0"
)

# Include routers
app.include_router(health.router)
app.include_router(items.router)


@app.get("/")
async def root():
    """Root endpoint returning a welcome message."""
    return {
        "message": "Welcome to the FastAPI Sample Application!",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

