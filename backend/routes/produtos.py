from fastapi import APIRouter, Body, UploadFile, File, Form, HTTPException
from database.conn_postgres import get_conn
import os
import uuid
import shutil
from typing import Optional

from services.produtos_services import (
      listar_produtos,
      buscar_produto,
      listar_produtos_por_categoria,
      cadastrar_novo_produto,
      editar_produto,
      listar_categorias,
      listar_produtos_recomendados,
      listar_fragrancias
)

router = APIRouter(prefix="/produtos", tags=["Produtos"])

UPLOAD_DIR = "static/products"

# Aviso para o Alisson do futuro:
# Se a rota começa com "listar" é pq retorna várias coisas/linhas
# Se a rota começa com "buscar" é pq só vai retornar uma coisa

@router.get("/")
def get_produtos():
    return listar_produtos()

@router.get("/categorias")
def get_categorias():
     return listar_categorias()

@router.get("/fragrancias")
def get_fragrancias():
     return listar_fragrancias()

@router.get("/{produto_id}")
def get_produto(produto_id: int):
      return buscar_produto(produto_id)

@router.get("/categoria/{categoria_id}")
def get_produtos_por_categoria(categoria_id: int):
     return listar_produtos_por_categoria(categoria_id)

@router.post("/novo_produto")
async def post_cadastrar_novo_produto(
     nome_produto: str = Form(...),
     marca: str = Form(...),
     descricao: str = Form(...),
     preco_unitario: float = Form(...),
     cod_categoria: int = Form(...),
     fragrancias: Optional[str] = Form("[]"), # Recebe como string JSON do FormData
     imagem: Optional[UploadFile] = File(None)
):
     url_imagem = None
     if imagem:
          os.makedirs(UPLOAD_DIR, exist_ok=True)
          extensao = os.path.splitext(imagem.filename)[1]
          nome_arquivo = f"{uuid.uuid4()}{extensao}"
          caminho_arquivo = os.path.join(UPLOAD_DIR, nome_arquivo)
          
          with open(caminho_arquivo, "wb") as buffer:
               shutil.copyfileobj(imagem.file, buffer)
          url_imagem = f"/{UPLOAD_DIR}/{nome_arquivo}"

     produto_dict = {
          "nome_produto": nome_produto,
          "marca": marca,
          "descricao": descricao,
          "preco_unitario": preco_unitario,
          "cod_categoria": cod_categoria,
          "url_imagem": url_imagem,
          "ativo": True,
          "fragrancias": eval(fragrancias) # Converte string "[1,2]" para lista
     }

     try:
         id_gerado = cadastrar_novo_produto(produto_dict)
         return {
              "status" : "sucesso",
              "mensagem" : f"Produto {nome_produto} cadastrado. Id: {id_gerado}"
         }
     except Exception as e:
         raise HTTPException(status_code=500, detail=f"Erro ao cadastrar produto: {str(e)}")


@router.put("/atualizar/{cod_produto}")
async def put_atualizar_produto(
    cod_produto: int,
    nome_produto: str = Form(...),
    marca: str = Form(...),
    descricao: str = Form(...),
    preco_unitario: float = Form(...),
    cod_categoria: int = Form(...),
    ativo: bool = Form(...),
    fragrancias: Optional[str] = Form("[]"),
    url_imagem_atual: Optional[str] = Form(None),
    imagem: Optional[UploadFile] = File(None)
):
      try:
            url_final = url_imagem_atual
            
            if imagem:
                # (Lógica de salvar novo arquivo similar à de cima...)
                extensao = os.path.splitext(imagem.filename)[1]
                nome_arquivo = f"{uuid.uuid4()}{extensao}"
                caminho_arquivo = os.path.join(UPLOAD_DIR, nome_arquivo)
                os.makedirs(UPLOAD_DIR, exist_ok=True)
                with open(caminho_arquivo, "wb") as buffer:
                    shutil.copyfileobj(imagem.file, buffer)
                url_final = f"/{UPLOAD_DIR}/{nome_arquivo}"

            dados_dict = {
                "nome_produto": nome_produto,
                "marca": marca,
                "descricao": descricao,
                "preco_unitario": preco_unitario,
                "cod_categoria": cod_categoria,
                "url_imagem": url_final,
                "ativo": ativo,
                "fragrancias": eval(fragrancias)
            }

            id_atualizado = editar_produto(cod_produto, dados_dict)

            if not id_atualizado:
                 raise HTTPException(status_code=404, detail="Produto não encontrado")
            return {
                 "status" : "sucesso",
                 "mensagem" : f"Produto {cod_produto} atualizado com sucesso"
            }

      except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar produto: {str(e)}")
      
@router.post("/produtos_recomendados")
def get_produtos_recomendados(carrinho: dict):
     produtos_carrinho = carrinho.get("cods", [])
     return listar_produtos_recomendados(produtos_carrinho)