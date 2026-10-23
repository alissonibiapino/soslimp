from pydantic import BaseModel, Field


class Fragrancia(BaseModel):
    cod_fragrancia: int = Field(..., description="Código único da fragrância")
    nome_fragrancia: str = Field(..., description="Nome da fragrância")


class ProdutoFragrancia(BaseModel):
    cod_produto: int = Field(..., description="Código do produto")
    cod_fragrancia: int = Field(..., description="Código da fragrância")
