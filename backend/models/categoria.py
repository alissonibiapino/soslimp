from pydantic import BaseModel, Field


class Categoria(BaseModel):
    cod_categoria: int = Field(..., description="Código único da categoria")
    categoria_produto: str = Field(..., description="Nome da categoria")
