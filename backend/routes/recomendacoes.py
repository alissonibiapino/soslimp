from fastapi import APIRouter
from services.recomendacoes_services import recomendar_produtos

router = APIRouter(prefix="/recomendacoes", tags=["Recomendações"])

@router.get("/produto/{cod_produto}")
def recomendar(cod_produto: int):
    return recomendar_produtos(cod_produto)
