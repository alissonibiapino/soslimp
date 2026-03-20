from fastapi import FastAPI
from routes import produtos, vendas, caixa

app = FastAPI(title="SOSLimp")

# Ligar o server xd
# uvicorn main:app --reload

# Inclusão das rotas
app.include_router(produtos.router)
app.include_router(vendas.router)
app.include_router(caixa.router)

@app.get('/')
def root():
    return {"Hello": "World"}