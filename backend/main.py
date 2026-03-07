from fastapi import FastAPI
from routes import produtos

app = FastAPI(title="SOSLimp")

# Ligar o server xd
# uvicorn main:app --reload

# Inclusão das rotas
app.include_router(produtos.router)

@app.get('/')
def root():
    return {"Hello": "World"}