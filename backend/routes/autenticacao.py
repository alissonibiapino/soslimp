from fastapi import APIRouter, HTTPException, status, Body
from services.autenticacao_services import verificar_credenciais, listar_lojas
import secrets

router = APIRouter(prefix="/autenticacao", tags=["Autenticação"])

@router.get("/lojas")
def get_lojas():
    return listar_lojas()

@router.post("/login")
def login(dados: dict = Body(...)):
    usuario = dados.get('usuario')
    senha = dados.get('senha')

    colaborador = verificar_credenciais(usuario, senha)
    
    if not colaborador:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha incorretos")
    
    return {
        "access_token": secrets.token_hex(16),
        "nome": colaborador['nome'],
        "cargo": colaborador['cargo'],
        "cod_colaborador": colaborador['cod_colaborador']
    }
