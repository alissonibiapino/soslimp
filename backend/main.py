from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import produtos, vendas, caixa, recomendacoes, autenticacao

app = FastAPI(title="SOSLimp")

# Ligar o server xd
# uvicorn main:app --reload

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Inclusão das rotas
app.include_router(produtos.router)
app.include_router(vendas.router)
app.include_router(caixa.router)
app.include_router(recomendacoes.router)
app.include_router(autenticacao.router)

@app.get('/')
def root():
    return {"Hello": "World"}