from pydantic import BaseModel, Field
from typing import Literal


class Loja(BaseModel):
    cod_loja: int = Field(..., description="Código único da loja")
    nome_loja: str = Field(..., description="Nome da loja")
    endereco: str = Field(..., description="Endereço da loja")
    bairro: str = Field(..., description="Bairro da loja")
    cidade: str = Field(..., description="Cidade da loja")
    cep: str = Field(..., description="CEP da loja")
    telefone: str = Field(..., description="Telefone da loja")
    email: str = Field(..., description="E-mail da loja")
    tipo_loja: Literal["MATRIZ", "FILIAL"] = Field(..., description="Tipo da loja")


class ColaboradorTrabalha(BaseModel):
    cod_loja: int = Field(..., description="Código da loja")
    cod_colaborador: int = Field(..., description="Código do colaborador")
