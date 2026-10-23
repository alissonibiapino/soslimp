const BASE_URL = "http://127.0.0.1:8000";

let produtosCache = [];
let estoqueCache = new Map();
let alertasCache = new Map();
let categoriasCache = [];
let filtroAtual = 'todos';
let filtroCategoria = null;

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

function fazerLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario_nome');
    localStorage.removeItem('usuario_cargo');
    localStorage.removeItem('cod_colaborador');
    localStorage.removeItem('loja_id');
    localStorage.removeItem('loja_nome');
    window.location.href = "login.html";
}

async function verificarStatusCaixa() {
    const cod_loja = localStorage.getItem('loja_id');
    if (!cod_loja) return;

    try {
        const response = await fetch(`${BASE_URL}/caixa/${cod_loja}`);
        const caixa = await response.json();

        if (!caixa) {
            const valorInicial = prompt("Nenhum caixa aberto para esta loja. Digite o valor inicial para abrir o caixa:", "0.00");

            if (valorInicial !== null) {
                const res = await fetch(`${BASE_URL}/caixa/abrir-caixa`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        cod_loja: parseInt(cod_loja),
                        valor_inicial: parseFloat(valorInicial.replace(',', '.'))
                    })
                });

                if (res.ok) {
                    localStorage.setItem('valorcaixa', parseFloat(valorInicial.replace(',', '.')))
                    alert("Caixa aberto com sucesso!");
                    location.reload();
                }
            } else {
                alert("É necessário abrir o caixa para operar o sistema.");
                fazerLogout();
            }
        } else {
            document.getElementById('menu-caixa-valor').textContent = `R$ ${caixa.valor_atual.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
            localStorage.setItem('cod_caixa', caixa.cod_caixa);
        }
    } catch (error) {
        console.error("Erro ao verificar caixa:", error);
    }
}

function infoEstoque(produto) {
    const item = estoqueCache.get(produto.cod_produto);
    return {
        qtd: item ? item.quantidade_atual : 0,
        minimo: item ? item.estoque_minimo : 0,
        atualizadoEm: item ? item.atualizado_em : null
    };
}

function statusEstoque(qtd, minimo) {
    if (qtd <= 0) return { chave: 'sem', texto: 'Sem estoque', classe: 'tag--cuidado' };
    if (qtd <= minimo) return { chave: 'baixo', texto: 'Estoque baixo', classe: 'tag--cuidado' };
    return { chave: 'ok', texto: 'OK', classe: 'tag--sucesso' };
}

async function carregarEstoque() {
    const tbody = document.getElementById('tabela-estoque-body');
    const cod_loja = localStorage.getItem('loja_id');

    try {
        const [respProdutos, respEstoque, respAlertas] = await Promise.all([
            fetch(`${BASE_URL}/produtos/`),
            fetch(`${BASE_URL}/estoque/${cod_loja}`),
            fetch(`${BASE_URL}/estoque/alertas/${cod_loja}`)
        ]);

        produtosCache = await respProdutos.json();
        const estoqueLista = await respEstoque.json();
        const alertas = await respAlertas.json();

        estoqueCache = new Map(estoqueLista.map(e => [e.cod_produto, e]));
        alertasCache = new Map((Array.isArray(alertas) ? alertas : []).map(a => [a.cod_produto, a]));

        preencherSelectProdutos();
        atualizarContadores();
        renderizarTabela();
    } catch (error) {
        console.error("Erro ao carregar estoque:", error);
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--cor-texto-secundario);">Não foi possível carregar o estoque.</td></tr>';
    }
}

async function carregarCategorias() {
    const cod_loja = localStorage.getItem('loja_id');

    try {
        const resp = await fetch(`${BASE_URL}/estoque/categorias/${cod_loja}`);
        categoriasCache = await resp.json();
        renderizarCategorias();
    } catch (error) {
        console.error("Erro ao carregar categorias:", error);
    }
}

function renderizarCategorias() {
    const nav = document.getElementById('categorias-estoque');
    if (!nav) return;

    nav.innerHTML = categoriasCache.map(cat => {
        const ativo = filtroCategoria === cat.cod_categoria;
        return `
            <button class="categoria-card${ativo ? ' active' : ''}" data-categoria="${cat.cod_categoria}"
                    aria-pressed="${ativo}">
                <span class="categoria-card__label">${cat.categoria_produto}</span>
                <span class="categoria-card__count">${cat.total_produtos} itens · ${cat.total_unidades} un.</span>
            </button>
        `;
    }).join('');
}

function limparFiltroCategoria() {
    filtroCategoria = null;
    document.querySelectorAll('#categorias-estoque .categoria-card').forEach(botao => {
        botao.classList.remove('active');
        botao.setAttribute('aria-pressed', 'false');
    });
}

function atualizarContadores() {
    const contagem = { todos: 0, baixo: 0, sem: 0, ok: 0 };

    produtosCache.forEach(prod => {
        const { qtd, minimo } = infoEstoque(prod);
        contagem.todos++;
        contagem[statusEstoque(qtd, minimo).chave]++;
    });

    document.getElementById('count-todos').textContent = `${contagem.todos} itens`;
    document.getElementById('count-baixo').textContent = `${contagem.baixo} itens`;
    document.getElementById('count-sem').textContent = `${contagem.sem} itens`;
    document.getElementById('count-ok').textContent = `${contagem.ok} itens`;
}

function renderizarTabela() {
    const tbody = document.getElementById('tabela-estoque-body');

    const linhas = produtosCache
        .map(prod => {
            const posicao = infoEstoque(prod);
            const status = statusEstoque(posicao.qtd, posicao.minimo);
            return { prod, ...posicao, status };
        })
        .filter(linha => (filtroAtual === 'todos' || linha.status.chave === filtroAtual)
            && (!filtroCategoria || linha.prod.cod_categoria === filtroCategoria))
        .sort((a, b) => {
            const prioridade = { sem: 0, baixo: 1, ok: 2 };
            return prioridade[a.status.chave] - prioridade[b.status.chave]
                || a.prod.nome_produto.localeCompare(b.prod.nome_produto);
        });

    if (!linhas.length) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--cor-texto-secundario);">Nenhum item neste filtro.</td></tr>';
        return;
    }

    tbody.innerHTML = linhas.map(({ prod, qtd, minimo, atualizadoEm, status }) => {
        const alerta = alertasCache.get(prod.cod_produto);
        const consumo = alerta && alerta.consumo_medio_diario != null
            ? Number(alerta.consumo_medio_diario).toLocaleString('pt-BR', { minimumFractionDigits: 2 })
            : '0,00';
        const diasRestantes = alerta && alerta.dias_restantes != null
            ? (Number(alerta.dias_restantes) > 90
                ? '> 90 dias'
                : `${Number(alerta.dias_restantes).toLocaleString('pt-BR', { minimumFractionDigits: 1 })} dias`)
            : 'sem vendas 30d';
        const imagem = prod.url_imagem
            ? `${BASE_URL}${prod.url_imagem}`
            : './assets/img/logo_soslimp.png';
        const atualizado = atualizadoEm
            ? new Date(atualizadoEm).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
            : '—';
        const pct = percentualEstoque(qtd, minimo);
        const qtdVisivel = Math.max(0, Number(qtd) || 0);
        const minimoVisivel = Math.max(0, Number(minimo) || 0);

        return `
            <tr>
                <td>
                    <div class="produto-info-cell">
                        <img src="${imagem}" alt="${prod.nome_produto}" class="produto-img-mini">
                        <span>${prod.nome_produto}</span>
                    </div>
                </td>
                <td><span class="tag">${prod.categoria_produto || 'Geral'}</span></td>
                <td>
                    <div class="estoque-barra">
                        <div class="estoque-barra__info">
                            <span class="estoque-valor">${qtdVisivel}</span>
                            <span class="estoque-barra__minimo">/ ${minimoVisivel} mín.</span>
                        </div>
                        <div class="estoque-barra__trilha" role="meter"
                             aria-label="Estoque atual em relação ao mínimo"
                             aria-valuemin="0" aria-valuemax="100" aria-valuenow="${Math.round(pct)}"
                             aria-valuetext="${qtdVisivel} de ${minimoVisivel} (mínimo)">
                            <div class="estoque-barra__preenchimento estoque-barra__preenchimento--${status.chave}" style="width: ${pct}%"></div>
                        </div>
                    </div>
                </td>
                <td>${consumo}</td>
                <td>${diasRestantes}</td>
                <td><span class="tag ${status.classe}">${status.texto}</span></td>
                <td>${atualizado}</td>
                <td style="text-align: center;">
                    <button class="btn-icon" onclick="prepararAjuste(${prod.cod_produto})" title="Ajustar estoque">
                        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path d="M12 4v16m8-8H4" />
                        </svg>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function percentualEstoque(qtd, minimo) {
    const q = Math.max(0, Number(qtd) || 0);
    const m = Math.max(0, Number(minimo) || 0);
    if (m === 0) return q > 0 ? 100 : 0;
    return Math.min((q / m) * 100, 100);
}

function preencherSelectProdutos() {
    const select = document.getElementById('produto_ajuste');
    const valorAtual = select.value;

    select.innerHTML = '<option value="">Selecione...</option>';
    [...produtosCache]
        .sort((a, b) => a.nome_produto.localeCompare(b.nome_produto))
        .forEach(prod => {
            const option = document.createElement('option');
            option.value = prod.cod_produto;
            option.textContent = prod.nome_produto;
            select.appendChild(option);
        });

    if (valorAtual) select.value = valorAtual;
    atualizarInfoEstoque();
}

function atualizarInfoEstoque() {
    const info = document.getElementById('info-estoque');
    const codProduto = parseInt(document.getElementById('produto_ajuste').value);
    const produto = produtosCache.find(p => p.cod_produto === codProduto);

    if (!produto) {
        info.textContent = 'Selecione um produto';
        return;
    }

    const { qtd, minimo } = infoEstoque(produto);
    info.textContent = `${produto.nome_produto} · Quantidade atual: ${qtd} · Estoque mínimo: ${minimo}`;
}

function prepararAjuste(codProduto) {
    document.getElementById('produto_ajuste').value = codProduto;
    atualizarInfoEstoque();
    document.getElementById('quantidade_ajuste').focus();
}

async function salvarAjuste(event) {
    event.preventDefault();

    const codProduto = parseInt(document.getElementById('produto_ajuste').value);
    const quantidade = parseInt(document.getElementById('quantidade_ajuste').value);
    const motivo = document.getElementById('motivo_ajuste').value.trim() || 'Ajuste manual';
    const codLoja = parseInt(localStorage.getItem('loja_id'));

    if (!codProduto) {
        alert('Selecione um produto.');
        return;
    }

    if (!quantidade) {
        alert('Informe uma quantidade diferente de zero.');
        return;
    }

    if (!confirm(`Registrar ${quantidade > 0 ? '+' : ''}${quantidade} unidade(s) no estoque?`)) return;

    const formData = new FormData();
    formData.append('cod_produto', codProduto);
    formData.append('cod_loja', codLoja);
    formData.append('quantidade', quantidade);
    formData.append('motivo', motivo);

    try {
        const response = await fetch(`${BASE_URL}/estoque/ajustar`, {
            method: 'POST',
            body: formData
        });

        const resultado = await response.json();

        if (resultado) {
            alert('Estoque ajustado com sucesso!');
            limparFormularioAjuste();
            carregarEstoque();
            carregarCategorias();
        } else {
            alert('Não foi possível ajustar o estoque.');
        }
    } catch (error) {
        console.error('Erro ao ajustar estoque:', error);
        alert('Erro ao ajustar estoque.');
    }
}

function limparFormularioAjuste() {
    document.getElementById('form-ajuste').reset();
    document.getElementById('motivo_ajuste').value = 'Ajuste manual';
    atualizarInfoEstoque();
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
    carregarEstoque();
    carregarCategorias();

    document.querySelectorAll('[data-filtro]').forEach(botao => {
        botao.addEventListener('click', () => {
            document.querySelectorAll('[data-filtro]').forEach(b => b.classList.remove('active'));
            botao.classList.add('active');
            filtroAtual = botao.dataset.filtro;

            if (filtroAtual === 'todos') {
                limparFiltroCategoria();
            }

            renderizarTabela();
        });
    });

    document.getElementById('categorias-estoque').addEventListener('click', (event) => {
        const botao = event.target.closest('[data-categoria]');
        if (!botao) return;

        const codCategoria = parseInt(botao.dataset.categoria);
        filtroCategoria = filtroCategoria === codCategoria ? null : codCategoria;

        document.querySelectorAll('#categorias-estoque .categoria-card').forEach(b => {
            const ativo = parseInt(b.dataset.categoria) === filtroCategoria;
            b.classList.toggle('active', ativo);
            b.setAttribute('aria-pressed', String(ativo));
        });

        renderizarTabela();
    });

    document.getElementById('produto_ajuste').addEventListener('change', atualizarInfoEstoque);
    document.getElementById('form-ajuste').addEventListener('submit', salvarAjuste);
    document.getElementById('btn-limpar-ajuste').addEventListener('click', limparFormularioAjuste);
});
