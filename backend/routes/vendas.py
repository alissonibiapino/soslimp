from fastapi import APIRouter, Body
from database.conn_postgres import get_conn

from services.vendas_services import (
    listar_vendas_do_dia,
    listar_vendas_do_dia_por_loja,
    listar_pedidos_do_dia,
    registrar_novo_pedido
)

router = APIRouter(prefix="/vendas", tags=["Vendas"])

@router.get("/")
def get_produtos():
    return listar_vendas_do_dia()

@router.get("/{cod_loja}")
def get_vendas_do_dia_por_loja(cod_loja: int):
      return listar_vendas_do_dia_por_loja(cod_loja)

@router.get("/pedidos-do-dia")
def get_pedidos_do_dia():
    return listar_pedidos_do_dia()

@router.post("/novo_pedido")
def post_registrar_novo_pedido(dados_do_pedido: dict = Body(...)):
     id_gerado = registrar_novo_pedido(dados_do_pedido)

     return {
          "status" : "sucesso",
          "mensagem:" : f"Produto {dados_do_pedido.get('nome_produto')}. Id: {id_gerado}"
     }
