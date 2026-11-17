from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class ProdutoBase(BaseModel):
    cod_produto: int = Field(..., description="Código único do produto")
    cod_categoria: Optional[int] = Field(None, description="Código da categoria")
    nome_produto: str = Field(..., description="Nome do produto")
    descricao: str = Field(..., description="Descrição do produto")
    marca: str = Field(..., description="Marca do produto")
    preco_unitario: float = Field(..., description="Preço unitário")
    url_imagem: Optional[str] = Field(None, description="URL da imagem do produto")
    ativo: bool = Field(True, description="Status do produto")

class Produto(ProdutoBase):
    criacao: datetime = Field(default_factory=datetime.now, description="Data de criação")
    modificacao: Optional[datetime] = Field(None, description="Data da última modificação")

class ProdutoCreate(ProdutoBase):
    cod_produto: Optional[int] = Field(None, description="Gerado pelo banco quando omitido")

class ProdutoUpdate(ProdutoBase):
    cod_produto: int = Field(..., description="Código do produto para atualização")
