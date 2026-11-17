from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class Estoque(BaseModel):
    cod_produto: int = Field(..., description="Código do produto")
    cod_loja: int = Field(..., description="Código da loja")
    quantidade_atual: int = Field(..., description="Quantidade atual em estoque")
    estoque_minimo: int = Field(..., description="Quantidade mínima de estoque")
    atualizado_em: datetime = Field(..., description="Data da última atualização")


class AjusteEstoque(BaseModel):
    cod_produto: int = Field(..., description="Código do produto")
    cod_loja: int = Field(..., description="Código da loja")
    quantidade: int = Field(..., description="Quantidade do ajuste (negativa para saída)")
    motivo: str = Field("Ajuste manual", description="Motivo do ajuste")


class MovimentacaoEstoque(BaseModel):
    cod_movimentacao: int = Field(..., description="Código único da movimentação")
    cod_produto: Optional[int] = Field(None, description="Código do produto")
    cod_loja: Optional[int] = Field(None, description="Código da loja")
    tipo_movimentacao: Literal["ENTRADA", "SAIDA", "AJUSTE"] = Field(..., description="Tipo da movimentação")
    quantidade: int = Field(..., description="Quantidade movimentada")
    cod_venda: Optional[int] = Field(None, description="Código da venda relacionada")
    motivo: Optional[str] = Field(None, description="Motivo da movimentação")
    data_movimentacao: datetime = Field(..., description="Data da movimentação")
