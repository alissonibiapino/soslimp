from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FormaPagamento(BaseModel):
    cod_forma_pag: int = Field(..., description="Código único da forma de pagamento")
    tipo_pagamento: str = Field(..., description="Tipo da forma de pagamento")


class RegistroPedido(BaseModel):
    cod_venda: int = Field(..., description="Código único da venda")
    cod_loja: Optional[int] = Field(None, description="Código da loja")
    cod_colaborador: Optional[int] = Field(None, description="Código do colaborador")
    cod_forma_pag: Optional[int] = Field(None, description="Código da forma de pagamento")
    valor_total: Optional[float] = Field(None, description="Valor total da venda")
    valor_recebido: Optional[float] = Field(None, description="Valor recebido")
    troco: Optional[float] = Field(None, description="Troco da venda")
    hora_do_registro: datetime = Field(..., description="Data e hora do registro")
    tipo_pagamento: Optional[str] = Field(None, description="Tipo da forma de pagamento")


class DetalhesPedido(BaseModel):
    cod_detalhes: int = Field(..., description="Código único do detalhe")
    cod_produto: Optional[int] = Field(None, description="Código do produto")
    quantidade: int = Field(..., description="Quantidade do produto")
    preco_unitario: Optional[float] = Field(None, description="Preço unitário")
    cod_venda: int = Field(..., description="Código da venda")
    cod_fragrancia: Optional[int] = Field(None, description="Código da fragrância")
    is_recomendacao: bool = Field(False, description="Indica se o item veio de recomendação")


class ItemPedido(BaseModel):
    cod_produto: int = Field(..., description="Código do produto")
    quantidade: int = Field(..., description="Quantidade do produto")
    cod_fragrancia: Optional[int] = Field(None, description="Código da fragrância")
    is_recomendacao: bool = Field(False, description="Indica se o item veio de recomendação")


class NovoPedido(BaseModel):
    model_config = {
        "json_schema_extra": {
            "example": {
                "cod_loja": 1,
                "cod_colaborador": 1,
                "cod_forma_pag": 4,
                "cod_caixa": 1,
                "valor_recebido": 100,
                "produtos": [
                    {"cod_produto": 1, "quantidade": 1, "cod_fragrancia": 1, "is_recomendacao": False}
                ]
            }
        }
    }

    cod_loja: int = Field(..., description="Código da loja")
    cod_colaborador: Optional[int] = Field(None, description="Código do colaborador")
    cod_forma_pag: int = Field(..., description="Código da forma de pagamento")
    cod_caixa: Optional[int] = Field(None, description="Código do caixa aberto")
    valor_recebido: float = Field(0, description="Valor recebido do cliente")
    produtos: list[ItemPedido] = Field(..., description="Itens do pedido")
