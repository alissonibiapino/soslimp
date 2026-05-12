from fastapi import APIRouter
from services.recomendacoes_services import recomendar_produto, recomendar_produtos_carrinho

router = APIRouter(prefix="/recomendacoes", tags=["Recomendações"])

@router.get("/produto/{cod_produto}")
def recomendar(cod_produto: int):
    return recomendar_produto(cod_produto)


@router.post("/carrinho")
def recomendar_carrinho(carrinho: dict):
    produtos_carrinho = carrinho.get("cods", [])
    return recomendar_produtos_carrinho(produtos_carrinho)