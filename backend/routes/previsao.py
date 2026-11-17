from fastapi import APIRouter

from models.previsao import PrevisaoEstoque
from services.previsao_services import treinar_modelo, prever_loja, prever_produto

router = APIRouter(prefix="/previsao", tags=["Previsão"])


@router.post("/treinar")
def post_treinar_modelo():
    return treinar_modelo()


@router.get("/estoque/{cod_loja}", response_model=list[PrevisaoEstoque])
def get_previsao_estoque_loja(cod_loja: int):
    return prever_loja(cod_loja)


@router.get("/estoque/{cod_loja}/{cod_produto}", response_model=PrevisaoEstoque)
def get_previsao_estoque_produto(cod_loja: int, cod_produto: int):
    return prever_produto(cod_loja, cod_produto)
