document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const usuario = document.getElementById('usuario').value;
    const senha = document.getElementById('senha').value;
    const selectLoja = document.getElementById('loja');
    const cod_loja = selectLoja.value;
    const nome_loja = selectLoja.options[selectLoja.selectedIndex].text;

    try {
        console.log(usuario, senha)
        const response = await fetch("http://localhost:8000/autenticacao/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ usuario, senha, cod_loja })
        });

        if (response.ok) {
            const data = await response.json();
            
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('usuario_nome', data.nome);
            localStorage.setItem('usuario_cargo', data.cargo);
            localStorage.setItem('cod_colaborador', data.cod_colaborador);
            localStorage.setItem('loja_id', cod_loja);
            localStorage.setItem('loja_nome', nome_loja);
            
            window.location.href = "index.html";
        } else {
            alert("Usuário ou senha incorretos");
        }
    } catch (error) {
        console.error("Erro na conexão:", error);
        alert("Usuário não existe");
    }
});

async function carregarLojas() {
    const selectLoja = document.getElementById('loja');
    if (!selectLoja) return;

    try {
        const response = await fetch("http://localhost:8000/autenticacao/lojas");
        const lojas = await response.json();

        lojas.forEach(loja => {
            const option = document.createElement('option');
            option.value = loja.cod_loja;
            option.textContent = loja.nome_loja;
            selectLoja.appendChild(option);
        });
    } catch (error) {
        console.error("Erro ao carregar lojas:", error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    carregarLojas();
    const token = localStorage.getItem('token');
    if (token) {
        window.location.href = "index.html";
    }
});
