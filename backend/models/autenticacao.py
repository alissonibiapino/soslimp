from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class Colaborador(BaseModel):
    cod_colaborador: int = Field(..., description="Código único do colaborador")
    cpf_cnpj: str = Field(..., description="CPF ou CNPJ do colaborador")
    nome: str = Field(..., description="Nome do colaborador")
    cargo: str = Field(..., description="Cargo do colaborador")
    data_admissao: date = Field(..., description="Data de admissão")
    data_demissao: Optional[date] = Field(None, description="Data de demissão")


class ColaboradorLoginBase(BaseModel):
    usuario: str = Field(..., max_length=20, description="Usuário de acesso")
    cod_colaborador: Optional[int] = Field(None, description="Colaborador vinculado ao login")


class ColaboradorLogin(ColaboradorLoginBase):
    cod_usuario_login: int = Field(..., description="Código único do login")
    senha_hash: Optional[str] = Field(None, max_length=255, description="Hash da senha")
    ultimo_login: Optional[datetime] = Field(None, description="Data do último login")


class LoginRequest(BaseModel):
    usuario: str = Field(..., description="Usuário de acesso")
    senha: str = Field(..., description="Senha do colaborador")


class LoginResponse(BaseModel):
    access_token: str = Field(..., description="Token de acesso")
    nome: str = Field(..., description="Nome do colaborador")
    cargo: str = Field(..., description="Cargo do colaborador")
    cod_colaborador: int = Field(..., description="Código do colaborador")
