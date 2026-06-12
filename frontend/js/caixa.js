const BASE_URL = "http://127.0.0.1:8000";

function exibirData() {
    const agora = new Date();
    const opcoes = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    let dataExtenso = new Intl.DateTimeFormat('pt-BR', opcoes).format(agora);
    dataExtenso = dataExtenso.charAt(0).toUpperCase() + dataExtenso.slice(1);
    document.getElementById('menu-data').textContent = dataExtenso.replace(',', '');
}

function atualizarRelogio() {
    const agora = new Date();
    document.getElementById('menu-hora').textContent = agora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

async function verificarStatusCaixa() {
    const cod_loja = localStorage.getItem('loja_id');
    if (!cod_loja) return;

    try {
        const response = await fetch(`${BASE_URL}/caixa/${cod_loja}`);
        const caixa = await response.json();

        if (caixa) {
            document.getElementById('menu-caixa-valor').textContent = `R$ ${caixa.valor_atual.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
        }
    } catch (error) {
        console.error("Erro ao verificar caixa:", error);
    }
}

async function carregarHistorico() {
    const tabelaBody = document.getElementById('tabela-caixa-body');
    const cod_loja = localStorage.getItem('loja_id');

    if (!tabelaBody || !cod_loja) return;

    try {
        const response = await fetch(`${BASE_URL}/caixa/historico/${cod_loja}`);
        const caixas = await response.json();

        tabelaBody.innerHTML = '';

        caixas.forEach(caixa => {
            const tr = document.createElement('tr');

            const abertura = Number(caixa.valor_inicial);
            const fechamento = Number(caixa.valor_atual);
            const diferenca = fechamento - abertura;

            tr.innerHTML = `
                <td>${new Date(caixa.data_abertura).toLocaleString('pt-BR')}</td>
                <td>${abertura.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
                <td>${fechamento.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
                <td style="${diferenca < 0 ? 'color: var(--cor-cuidado)' : ''}">
                    ${diferenca.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                </td>
                <td>
                    <span class="tag ${caixa.status_caixa === 'ABERTO' ? 'tag--sucesso' : 'tag--cuidado'}">
                        ${caixa.status_caixa}
                    </span>
                </td>
            `;

            tabelaBody.appendChild(tr);
        });

    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = "login.html";
        return;
    }

    document.getElementById('loja-nome').textContent = localStorage.getItem('loja_nome');

    exibirData();
    atualizarRelogio();
    setInterval(atualizarRelogio, 60000);
    verificarStatusCaixa();
    carregarHistorico();

});
