from fastapi import APIRouter, Form

from models.estoque import AjusteEstoque, Estoque
from services.estoque_services import listar_estoque_por_loja, listar_estoque, ajustar_estoque_manualmente, listar_alertas_reposicao

router = APIRouter(prefix="/estoque", tags=["Estoque"])

@router.get("/", response_model=list[Estoque])
def get_listar_estoque():
    return listar_estoque()

@router.get("/{cod_loja}", response_model=list[Estoque])
def get_estoque_por_loja(cod_loja: int):
    return listar_estoque_por_loja(cod_loja)

@router.post("/ajustar")
def ajustar_estoque(
    cod_produto: int = Form(...),
    cod_loja: int = Form(...),
    quantidade: int = Form(...),
    motivo: str = Form("Ajuste manual")
):
    ajuste = AjusteEstoque(
        cod_produto=cod_produto,
        cod_loja=cod_loja,
        quantidade=quantidade,
        motivo=motivo
    )
    return ajustar_estoque_manualmente(ajuste)

@router.get("/alertas/{cod_loja}")
def get_alertas_reposicao(cod_loja: int):
    return listar_alertas_reposicao(cod_loja)
