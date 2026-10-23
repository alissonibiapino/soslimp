from pydantic import BaseModel, Field


class RecomendacaoCarrinho(BaseModel):
    cods: list[int] = Field(default_factory=list, description="Códigos dos produtos no carrinho")
