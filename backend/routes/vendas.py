from fastapi import APIRouter

from models.venda import DetalhesPedido, NovoPedido, RegistroPedido
from services.vendas_services import (
    listar_vendas_do_dia,
    listar_vendas_do_dia_por_loja,
    listar_pedidos_do_dia,
    registrar_novo_pedido
)

router = APIRouter(prefix="/vendas", tags=["Vendas"])

@router.get("/", response_model=list[RegistroPedido])
def get_produtos():
    return listar_vendas_do_dia()

@router.get("/pedidos-do-dia", response_model=list[DetalhesPedido])
def get_pedidos_do_dia():
    return listar_pedidos_do_dia()

@router.get("/{cod_loja}", response_model=list[RegistroPedido])
def get_vendas_do_dia_por_loja(cod_loja: int):
      return listar_vendas_do_dia_por_loja(cod_loja)

@router.post("/novo_pedido")
def post_registrar_novo_pedido(dados_do_pedido: NovoPedido):
     id_gerado = registrar_novo_pedido(dados_do_pedido)

     return {
          "status" : "sucesso",
          "mensagem" : f"Pedido {id_gerado} registrado com sucesso"
     }
