const BASE_URL = "http://127.0.0.1:8000";

let produtosCache = [];
let estoqueCache = new Map();
let alertasCache = new Map();
let previsaoCache = new Map();
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

function formatarPrevisao(codProduto) {
    const previsao = previsaoCache.get(codProduto);

    if (!previsao) {
        return '<span style="color: var(--cor-texto-secundario);">sem previsão</span>';
    }

    if (previsao.dias_restantes == null) {
        return '<span class="tag tag--neutro">Sem consumo</span>';
    }

    const estilos = {
        CRITICO: { classe: 'tag--cuidado', valor: 'previsao-valor--critico', texto: 'Crítico' },
        ATENCAO: { classe: 'tag--neutro', valor: 'previsao-valor--atencao', texto: 'Atenção' },
        OK: { classe: 'tag--sucesso', valor: 'previsao-valor--ok', texto: 'OK' }
    };
    const estilo = estilos[previsao.risco] || estilos.OK;
    const dias = Number(previsao.dias_restantes).toLocaleString('pt-BR', { minimumFractionDigits: 1 });

    return `<strong class="previsao-valor ${estilo.valor}">~${dias} dias</strong> <span class="tag ${estilo.classe}">${estilo.texto}</span>`;
}

async function carregarEstoque() {
    const tbody = document.getElementById('tabela-estoque-body');
    const cod_loja = localStorage.getItem('loja_id');

    try {
        const [respProdutos, respEstoque, respAlertas, respPrevisao] = await Promise.all([
            fetch(`${BASE_URL}/produtos/`),
            fetch(`${BASE_URL}/estoque/${cod_loja}`),
            fetch(`${BASE_URL}/estoque/alertas/${cod_loja}`),
            fetch(`${BASE_URL}/previsao/estoque/${cod_loja}`)
        ]);

        produtosCache = await respProdutos.json();
        const estoqueLista = await respEstoque.json();
        const alertas = await respAlertas.json();

        estoqueCache = new Map(estoqueLista.map(e => [e.cod_produto, e]));
        alertasCache = new Map((Array.isArray(alertas) ? alertas : []).map(a => [a.cod_produto, a]));

        // 503 = modelo ainda não treinado; a tabela continua funcionando sem previsão.
        if (respPrevisao.ok) {
            const previsoes = await respPrevisao.json();
            previsaoCache = new Map(previsoes.map(p => [p.cod_produto, p]));
        } else {
            previsaoCache = new Map();
        }

        preencherSelectProdutos();
        atualizarContadores();
        renderizarCategorias();
        renderizarTabela();
    } catch (error) {
        console.error("Erro ao carregar estoque:", error);
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--cor-texto-secundario);">Não foi possível carregar o estoque.</td></tr>';
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

    const todas = `
        <button class="categoria-card${filtroCategoria === null ? ' active' : ''}" data-categoria="todas"
                aria-pressed="${filtroCategoria === null}">
            <span class="categoria-card__label">Todas categorias</span>
            <span class="categoria-card__count">${produtosCache.length} itens</span>
        </button>
    `;
    nav.innerHTML = todas + categoriasCache.map(cat => {
        const ativo = filtroCategoria === cat.cod_categoria;
        return `
            <button class="categoria-card${ativo ? ' active' : ''}" data-categoria="${cat.cod_categoria}"
                    aria-pressed="${ativo}">
                <span class="categoria-card__label">${cat.categoria_produto}</span>
                <span class="categoria-card__count">${cat.total_produtos} itens</span>
            </button>
        `;
    }).join('');
}

function atualizarAtivosCategorias() {
    document.querySelectorAll('#categorias-estoque .categoria-card').forEach(b => {
        const ativo = b.dataset.categoria === 'todas'
            ? filtroCategoria === null
            : parseInt(b.dataset.categoria) === filtroCategoria;
        b.classList.toggle('active', ativo);
        b.setAttribute('aria-pressed', String(ativo));
    });
}

function limparFiltroCategoria() {
    filtroCategoria = null;
    atualizarAtivosCategorias();
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

    document.getElementById('count-baixo').classList.toggle('count-alerta', contagem.baixo > 0);
    document.getElementById('count-sem').classList.toggle('count-alerta', contagem.sem > 0);
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
            // Sem estoque no topo mesmo sem previsão; depois urgência ML; desempate alfabético.
            const blocos = l => l.status.chave === 'sem' ? 0 : 1;
            const dias = l => {
                const previsao = previsaoCache.get(l.prod.cod_produto);
                return previsao?.dias_restantes != null ? previsao.dias_restantes : Number.MAX_SAFE_INTEGER;
            };
            return blocos(a) - blocos(b)
                || dias(a) - dias(b)
                || a.prod.nome_produto.localeCompare(b.prod.nome_produto);
        });

    if (!linhas.length) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--cor-texto-secundario);">Nenhum item neste filtro.</td></tr>';
        return;
    }

    tbody.innerHTML = linhas.map(({ prod, qtd, minimo, status }) => {
        const alerta = alertasCache.get(prod.cod_produto);
        const consumo = alerta && alerta.consumo_medio_diario != null
            ? Number(alerta.consumo_medio_diario).toLocaleString('pt-BR', { minimumFractionDigits: 2 })
            : '0,00';
        const imagem = prod.url_imagem
            ? `${BASE_URL}${prod.url_imagem}`
            : './assets/img/logo_soslimp.png';
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
                <td class="consumo-dia">${consumo}</td>
                <td>${formatarPrevisao(prod.cod_produto)}</td>
                <td style="text-align: center;">
                    <button class="btn-icon" onclick="prepararAjuste(${prod.cod_produto})" title="Ajustar estoque">
                        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7M18.5 2.5a2.121 2.121 0 113 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
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
    document.getElementById('dialog-ajuste').showModal();
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
            mostrarToast('Estoque ajustado com sucesso!');
            limparFormularioAjuste();
            carregarEstoque();
            carregarCategorias();
        } else {
            alert('Não foi possível ajustar o estoque.');
        }    } catch (error) {
        console.error('Erro ao ajustar estoque:', error);
        alert('Erro ao ajustar estoque.');
    }
}

function limparFormularioAjuste() {
    document.getElementById('dialog-ajuste').close();
    document.getElementById('form-ajuste').reset();
    document.getElementById('motivo_ajuste').value = 'Ajuste manual';
    atualizarInfoEstoque();
}

const btnRetreinar = document.getElementById('btn-retreinar');
const btnRetreinarLabel = document.getElementById('btn-retreinar-label');
const dialogRetreinar = document.getElementById('dialog-retreinar');
const btnConfirmarRetreino = document.getElementById('btn-confirmar-retreino');
const overlayTreino = document.getElementById('overlay-treino');

async function retreinarModelo() {
    btnRetreinar.disabled = true;
    btnRetreinarLabel.textContent = 'TREINANDO...';
    overlayTreino.hidden = false;

    try {
        const response = await fetch(`${BASE_URL}/previsao/treinar`, { method: 'POST' });

        if (response.status === 409) {
            alert('Já existe um treino em andamento. Aguarde alguns minutos.');
            return;
        }

        if (!response.ok) {
            const detalhe = await response.json().catch(() => null);
            alert(`Falha no retreino: ${detalhe?.detail || 'erro no servidor'}.`);
            return;
        }

        const resultado = await response.json();
        const metricas = resultado.metricas_holdout || {};
        alert(
            'Modelo retreinado com sucesso!\n' +
            `Última semana do treino: ${resultado.ultima_semana_treino}\n` +
            `Validação (holdout de ${metricas.semanas_holdout} semanas): MAE ${Number(metricas.mae).toFixed(2)} · RMSE ${Number(metricas.rmse).toFixed(2)}`
        );

        carregarEstoque();
    } catch (error) {
        console.error('Erro ao retreinar modelo:', error);
        alert('Erro de conexão ao retreinar o modelo.');
    } finally {
        overlayTreino.hidden = true;
        btnRetreinar.disabled = false;
        btnRetreinarLabel.textContent = 'RETREINAR PREVISÃO';
    }
}

function configurarRetreino() {
    // Ação restrita ao gestor; gated no frontend (o backend ainda expõe o endpoint sem cargo).
    if (localStorage.getItem('usuario_cargo') !== 'MICROEMPRESARIO') {
        btnRetreinar.style.display = 'none';
        return;
    }

    btnRetreinar.addEventListener('click', () => dialogRetreinar.showModal());
    document.getElementById('btn-cancelar-retreino').addEventListener('click', () => dialogRetreinar.close());
    btnConfirmarRetreino.addEventListener('click', () => {
        dialogRetreinar.close();
        retreinarModelo();
    });
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

        const raw = botao.dataset.categoria;
        const codCategoria = raw === 'todas' ? null : parseInt(raw);
        filtroCategoria = (codCategoria !== null && filtroCategoria === codCategoria) ? null : codCategoria;

        atualizarAtivosCategorias();
        renderizarTabela();
    });

    document.getElementById('produto_ajuste').addEventListener('change', atualizarInfoEstoque);
    document.getElementById('form-ajuste').addEventListener('submit', salvarAjuste);
    document.getElementById('btn-limpar-ajuste').addEventListener('click', limparFormularioAjuste);
    configurarRetreino();
});
