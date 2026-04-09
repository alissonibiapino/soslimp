from fastapi import APIRouter, Body
from database.conn_postgres import get_conn

from services.produtos_services import (
      listar_produtos,
      buscar_produto,
      listar_produtos_por_categoria,
      cadastrar_novo_produto,
      editar_produto,
      listar_categorias
)

router = APIRouter(prefix="/produtos", tags=["Produtos"])

# Aviso para o Alisson do futuro:
# Se a rota começa com "listar" é pq retorna várias coisas/linhas
# Se a rota começa com "buscar" é pq só vai retornar uma coisa

@router.get("/")
def get_produtos():
    return listar_produtos()

@router.get("/categorias")
def get_categorias():
     return listar_categorias()

@router.get("/{produto_id}")
def get_produto(produto_id: int):
      return buscar_produto(produto_id)

@router.get("/categoria/{categoria_id}")
def get_produtos_por_categoria(categoria_id: int):
     return listar_produtos_por_categoria(categoria_id)

@router.post("/novo_produto")
def post_cadastrar_novo_produto(produto: dict = Body(...)):
     id_gerado = cadastrar_novo_produto(produto)

     return {
          "status" : "sucesso",
          "mensagem:" : f"Produto {produto.get('nome_produto')}. Id: {id_gerado}"
     }

@router.put("/atualizar/{cod_produto}")
def put_atualizar_produto(cod_produto: int, dados: dict = Body(...)):
      try:
            id_atualizado = editar_produto(cod_produto, dados)

            if not id_atualizado:
                 return print("Produto não encontrado")
            return {
                 "status" : "sucesso",
                 "mensagem" : f"Produto {cod_produto} atualizado com sucesso"
            }

      except Exception as e:
            return print(f"Erro no banco: {e}")