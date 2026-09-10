from ai_code_agent.core import (
    asynccontextmanager,
    FastAPI,
    create_db_and_tables,
    build_graph,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Load shared resources (e.g., DB connection pool, ML models)
    print("Starting up...")
    create_db_and_tables()
    app.state.graph = build_graph()
    yield
    # 2. Shutdown: Clean up resources (e.g., close DB connections)
    print("Shutting down...")
