from fastapi import APIRouter, Body
from database.conn_postgres import get_conn

from services.caixa_services import (
    caixa_atual,
    abrir_novo_caixa,
    fechar_caixa_dia,
    listar_historico_caixa
)

router = APIRouter(prefix="/caixa", tags=["Caixa"])

@router.post("/abrir-caixa")
def abrir_caixa(dados_caixa: dict = Body(...)):
    cod_caixa = abrir_novo_caixa(dados_caixa['cod_loja'], dados_caixa['valor_inicial'])
    return {"status": "Caixa aberto com sucesso", "cod_caixa": cod_caixa}

@router.post("/fechar-caixa")
def fechar_caixa(dados_caixa: dict = Body(...)):
    return fechar_caixa_dia(dados_caixa['cod_caixa'], dados_caixa['valor_fechamento'])

@router.get("/{cod_loja}")
def get_produtos(cod_loja: int):
    return caixa_atual(cod_loja)

@router.get("/historico/{cod_loja}")
def get_historico(cod_loja: int):
    return listar_historico_caixa(cod_loja)