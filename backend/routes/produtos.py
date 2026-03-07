from fastapi import APIRouter
from database.conn_postgres import get_conn
from psycopg2.extras import RealDictCursor

from services.produtos_services import (
      listar_produtos,
      buscar_produto,
      listar_produtos_por_categoria
)

router = APIRouter(prefix="/produtos", tags=["Produtos"])

# Aviso para o Alisson do futuro:
# Se a rota começa com "listar" é pq retorna várias coisas/linhas
# Se a rota começa com "buscar" é pq só vai retornar uma coisa

@router.get("/")
def get_produtos():
    return listar_produtos()


@router.get("/{produto_id}")
def get_produto(produto_id: int):
      return buscar_produto(produto_id)


@router.get("/categoria/{categoria_id}")
def get_produtos_por_categoria(categoria_id: int):
     return listar_produtos_por_categoria(categoria_id)