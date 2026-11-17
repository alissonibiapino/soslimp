from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class Caixa(BaseModel):
    cod_caixa: int = Field(..., description="Código único do caixa")
    data_abertura: datetime = Field(..., description="Data de abertura")
    valor_inicial: float = Field(..., description="Valor inicial")
    valor_atual: float = Field(..., description="Valor atual")
    valor_final: Optional[float] = Field(None, description="Valor final")
    diferenca: Optional[float] = Field(None, description="Diferença do fechamento")
    status_caixa: Literal["ABERTO", "FECHADO"] = Field(..., description="Status do caixa")
    cod_loja: int = Field(..., description="Código da loja")


class AberturaCaixa(BaseModel):
    cod_loja: int = Field(..., description="Código da loja")
    valor_inicial: float = Field(..., description="Valor inicial do caixa")


class FechamentoCaixa(BaseModel):
    cod_caixa: int = Field(..., description="Código do caixa")
    valor_fechamento: float = Field(..., description="Valor de fechamento do caixa")


class MovimentacaoCaixa(BaseModel):
    cod_movimentacao: int = Field(..., description="Código da movimentação")
    cod_caixa: Optional[int] = Field(None, description="Código do caixa")
    valor: Optional[float] = Field(None, description="Valor da movimentação")
    data_movimentacao: datetime = Field(..., description="Data da movimentação")
    cod_venda: Optional[int] = Field(None, description="Código da venda relacionada")
