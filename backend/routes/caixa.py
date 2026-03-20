from fastapi import APIRouter, Body
from database.conn_postgres import get_conn

from services.caixa_services import (
    caixa_atual
)

router = APIRouter(prefix="/caixa", tags=["Caixa"])

@router.get("/{cod_loja}")
def get_produtos(cod_loja: int):
    return caixa_atual(cod_loja)