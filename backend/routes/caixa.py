from fastapi import APIRouter

from models.caixa import AberturaCaixa, Caixa, FechamentoCaixa
from services.caixa_services import (
    caixa_atual,
    abrir_novo_caixa,
    fechar_caixa_dia,
    listar_historico_caixa
)

router = APIRouter(prefix="/caixa", tags=["Caixa"])

@router.post("/abrir-caixa")
def abrir_caixa(dados_caixa: AberturaCaixa):
    cod_caixa = abrir_novo_caixa(dados_caixa)
    return {"status": "Caixa aberto com sucesso", "cod_caixa": cod_caixa}

@router.post("/fechar-caixa")
def fechar_caixa(dados_caixa: FechamentoCaixa):
    return fechar_caixa_dia(dados_caixa)

@router.get("/{cod_loja}", response_model=Caixa | None)
def get_produtos(cod_loja: int):
    return caixa_atual(cod_loja)

@router.get("/historico/{cod_loja}", response_model=list[Caixa])
def get_historico(cod_loja: int):
    return listar_historico_caixa(cod_loja)
