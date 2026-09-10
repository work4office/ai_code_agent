from ai_code_agent.middleware import FastAPI, CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def register_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
