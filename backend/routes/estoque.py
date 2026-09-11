from fastapi import APIRouter, Body
from database.conn_postgres import get_conn

from services.estoque_services import listar_estoque_por_loja, listar_estoque

router = APIRouter(prefix="/estoque", tags=["Estoque"])

@router.get("/")
def get_listar_estoque():
    return listar_estoque()

@router.get("/{cod_loja}")
def get_estoque_por_loja(cod_loja: int):
    return listar_estoque_por_loja(cod_loja)
