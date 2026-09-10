import ssl

ssl._create_default_https_context = ssl._create_unverified_context
from ai_code_agent import FastAPI, lifespan, root_router, register_middleware

app = FastAPI(title="Ai Code Agent", lifespan=lifespan, root_path="/api/v1")
app.include_router(root_router)
register_middleware(app)
