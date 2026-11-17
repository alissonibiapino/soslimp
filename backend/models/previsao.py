from pydantic import BaseModel, Field
from typing import Literal
from datetime import date


class PrevisaoEstoque(BaseModel):
    cod_produto: int = Field(..., description="Código do produto")
    nome_produto: str = Field(..., description="Nome do produto")
    quantidade_atual: int = Field(..., description="Quantidade atual em estoque")
    consumo_previsto_diario: float = Field(..., description="Consumo diário previsto para a próxima semana")
    dias_restantes: float | None = Field(None, description="Dias estimados até acabar o estoque")
    data_ruptura_estimada: date | None = Field(None, description="Data estimada de ruptura do estoque")
    risco: Literal["CRITICO", "ATENCAO", "OK"] = Field(..., description="Nível de risco de ruptura")
