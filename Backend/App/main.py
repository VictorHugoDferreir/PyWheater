from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Api.endpoints import clima

app = FastAPI(title="API de Clima", version="1.0.0")

#Configuração de CORS (segurança de recursos compartilhados entre origens)
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#configuração das rotas
app.include_router(clima.router, prefix="/api/clima", tags=["Clima"])

@app.get("/")
def raiz():
    return {"mensagem": "API de Clima Online!"}



