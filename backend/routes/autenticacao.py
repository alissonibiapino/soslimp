from fastapi import APIRouter, HTTPException, status
from services.autenticacao_services import verificar_credenciais, listar_lojas
from models.autenticacao import LoginRequest, LoginResponse
from models.loja import Loja
import secrets

router = APIRouter(prefix="/autenticacao", tags=["Autenticação"])

@router.get("/lojas", response_model=list[Loja])
def get_lojas():
    return listar_lojas()

@router.post("/login", response_model=LoginResponse)
def login(dados: LoginRequest):
    colaborador = verificar_credenciais(dados)
    
    if not colaborador:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha incorretos")
    
    return LoginResponse(
        access_token=secrets.token_hex(16),
        nome=colaborador.nome,
        cargo=colaborador.cargo,
        cod_colaborador=colaborador.cod_colaborador
    )
