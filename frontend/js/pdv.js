// Variaveis
let carrinho = [];
let metodoPagamento = 'pix';

// Funções do menu

function exibirData() {
    const agora = new Date();

    const opcoes = {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    };

    let dataExtenso = new Intl.DateTimeFormat('pt-BR', opcoes).format(agora);
    dataExtenso = dataExtenso.charAt(0).toUpperCase() + dataExtenso.slice(1);
    dataExtenso = dataExtenso.replace(',', '');

    document.getElementById('menu-data').textContent = dataExtenso;
}

// Categorias
async function carregarCategorias() {
    const nav = document.getElementById('categorias-nav')

    try {
        const response = await fetch("http://127.0.0.1:8000/produtos/categorias");
        const categorias = await response.json()

        categorias.forEach(cat => {
            const button = document.createElement('button');
            button.className = 'categoria-card';
            button.dataset.category = cat.cod_categoria;

            button.innerHTML = `
                <div class="categoria-card__icone">
                    <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                        <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                </div>
                <span class="categoria-card__label">${cat.categoria_produto}</span>
                <span class="categoria-card__count">${cat.total_produtos.toString().padStart(2, '0')} itens</span>
            `;

            button.addEventListener('click', () => {
                document.querySelectorAll('.categoria-card').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                carregarProdutos(cat.cod_categoria);
            })

            nav.appendChild(button);
        });

        const btnTodas = document.querySelector('[data-category="todas"]');
        btnTodas.addEventListener('click', () => {
            document.querySelectorAll('.categoria-card').forEach(btn => btn.classList.remove('active'));
            btnTodas.classList.add('active');

            carregarProdutos();
        });

    } catch (error) {
        console.error("Erro nas categorias:", error)
    }
}

// Produtos
async function carregarProdutos(categoriaId = null) {
    const produtos_grid = document.getElementById('produtos-grid')
    produtos_grid.innerHTML = ''


    try {
        let url = "http://127.0.0.1:8000/produtos";

        if (categoriaId) {
            url = `http://127.0.0.1:8000/produtos/categoria/${categoriaId}`;
        }

        const response = await fetch(url);
        const produtos = await response.json()

        produtos.forEach(prod => {
            const article = document.createElement('article');
            article.className = 'produto-card';

            article.innerHTML = `
                <div class="produto-card__imagem_box">
                    <img class="produto-card__imagem" />
                </div>
                <div class="produto-card__corpo">
                    <h3 class="produto-card__nome">${prod.nome_produto}</h3>
                    <span class="produto-card__preco">${prod.preco_unitario.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span>
                </div>
            `;

            article.addEventListener('click', () => adicionarAoCarrinho(prod));
            produtos_grid.appendChild(article)

        });

    } catch (error) {
        console.error("Erro nas categorias:", error)
        produtos_grid.innerHTML = '<p>Erro ao carregar produtos.</p>';
    }
}

function atualizarCarrinhoHTML() {
    const listaVenda = document.getElementById('venda-items');
    listaVenda.innerHTML = '';

    carrinho.forEach(item => {
        const li = document.createElement('li');
        li.className = 'venda-item';
        li.dataset.id = item.id;

        li.innerHTML = `
            <div class="venda-item__qty">
                <button class="qty-btn" onclick="alterarQuantidade('${item.id}', -1)">-</button>
                <span class="qty-value">${item.quantidade}</span>
                <button class="qty-btn" onclick="alterarQuantidade(${item.id}, 1)">+</button>
            </div>
            <div class="venda-item__info">
                <span class="venda-item__nome">${item.nome}</span>
                <div class="venda-item__tags">
                    <span class="tag tag--blue">${item.marca}</span>
                </div>
            </div>
            <span class="venda-item__preco">R$ ${(item.preco * item.quantidade).toFixed(2).replace('.', ',')}</span>
        `;
        listaVenda.appendChild(li);
    });
    atualizarTotais();
}

function adicionarAoCarrinho(produto) {
    const itemExistente = carrinho.find(item => item.id === produto.cod_produto);

    if (itemExistente) {
        itemExistente.quantidade += 1;
    } else {
        carrinho.push({
            id: produto.cod_produto,
            nome: produto.nome_produto,
            preco: produto.preco_unitario,
            marca: produto.marca || 'SOSLimp',
            quantidade: 1
        });
    }
    atualizarCarrinhoHTML();
    buscarRecomendacoes()
    atualizarTotais();
}

function alterarQuantidade(id, delta) {
    const item = carrinho.find(item => Number(item.id) === Number(id));
    if (!item) return;

    item.quantidade += delta;

    if (item.quantidade <= 0) {
        carrinho = carrinho.filter(i => Number(i.id) !== Number(id));
    }

    atualizarCarrinhoHTML();
    buscarRecomendacoes();
    atualizarTotais();
}

async function buscarRecomendacoes() {
    if (carrinho.length === 0) {
        document.getElementById('comprado-junto__lista').innerHTML = 'Nenhum produto selecionado.';
        return;
    }

    const cods = carrinho.map(produto => produto.id)

    try {
        const response = await fetch("http://127.0.0.1:8000/produtos/produtos_recomendados", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ cods: cods })
        });

        const produtosCompletos = await response.json();
        if (produtosCompletos.length === 0) {
            document.getElementById('comprado-junto__lista').innerHTML = '<span>Esse produto ainda não possui recomendações.</span>';
        } else {
            carregarRecomendacoes(produtosCompletos);
        }
    } catch (error) {
        console.log("Erro:", error);
    }

}

async function carregarRecomendacoes(produtosCompletos) {
    const recomendacao_lista = document.getElementById('comprado-junto__lista')
    recomendacao_lista.innerHTML = ''

    produtosCompletos.forEach(prod => {
        const article = document.createElement('li');
        article.className = 'comprado-junto__item';

        article.innerHTML = `
            <div class="comprado-junto__item__info">
                <span class="comprado-junto__item__nome">${prod.nome_produto}</span>
                <div class="comprado-junto__item__tags">
                    <span class="comprado-junto__item_marca">${prod.marca}</span>
                </div>
            </div>
            <span class="comprado-junto__item__preco">${prod.preco_unitario.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span>
        `;

        article.addEventListener('click', () => adicionarAoCarrinho(prod));
        recomendacao_lista.appendChild(article)
    });
}

function atualizarTotais() {
    const subtotal = carrinho.reduce((acc, item) => acc + (item.preco * item.quantidade), 0);
    const desconto = 0;
    const total = subtotal - desconto;

    const formatar = (v) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    document.getElementById('subtotal').textContent = formatar(subtotal);
    document.getElementById('total').textContent = formatar(total);
    document.getElementById('desconto').textContent = formatar(desconto);

    const btnRegistrar = document.getElementById('btn-registrar-venda');
    const btnLimpar = document.getElementById('btn-limpar-venda');
    btnRegistrar.disabled = (carrinho.length === 0 || !metodoPagamento);
    btnLimpar.disabled = (carrinho.length === 0 || !metodoPagamento);

}
document.querySelectorAll('.metodo-pagamento').forEach(botao => {
    botao.addEventListener('click', () => {
        document.querySelectorAll('.metodo-pagamento').forEach(b => {
            b.classList.remove('metodo-pagamento--ativo');
        });

        botao.classList.add('metodo-pagamento--ativo');

        metodoPagamento = botao.dataset.method;
        atualizarTotais();
    });
});

document.getElementById('btn-limpar-venda').addEventListener('click', () => {
    if (confirm("Deseja realmente limpar toda a venda?")) {
        carrinho = [];
        atualizarCarrinhoHTML();
        atualizarTotais();
        document.querySelectorAll('.metodo-pagamento').forEach(b => {
            b.classList.remove('metodo-pagamento--ativo');
        });
        if (typeof buscarRecomendacoes === "function") buscarRecomendacoes();
    }
});

document.getElementById('btn-registrar-venda').addEventListener('click', () => {
    if (confirm("Deseja confirmar a venda?")) {
        realizarVenda()
    }
});



// Verificar login
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');

    if (!token) {
        window.location.href = "login.html";
    }

    const nomeUsuario = localStorage.getItem('usuario_nome');
    const cargoUsuario = localStorage.getItem('usuario_cargo');
    const nomeLoja = localStorage.getItem('loja_nome');

    document.getElementById('operador-nome').textContent = nomeUsuario;
    document.getElementById('operador-cargo').textContent = cargoUsuario;
    document.getElementById('loja-nome').textContent = nomeLoja;
    verificarStatusCaixa();
});

// Deslogar
document.getElementById('btn-logout-acao').addEventListener('click', () => {
    let result = confirm("Deseja realmente sair?");

    if (result) {
        fazerLogout()
    } else {
        return
    }
});

function fazerLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario_nome');
    localStorage.removeItem('usuario_cargo');
    localStorage.removeItem('cod_colaborador');
    localStorage.removeItem('loja_id');
    localStorage.removeItem('loja_nome');
    window.location.href = "login.html";
}


// Caixaaaaa
async function verificarStatusCaixa() {
    const cod_loja = localStorage.getItem('loja_id');

    try {
        const response = await fetch(`http://127.0.0.1:8000/caixa/${cod_loja}`);
        const caixa = await response.json();

        if (!caixa) {
            const valorInicial = prompt("Nenhum caixa aberto para esta loja. Digite o valor inicial para abrir o caixa:", "0.00");

            if (valorInicial !== null) {
                const res = await fetch("http://127.0.0.1:8000/caixa/abrir-caixa", {
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
                }
            } else {
                alert("É necessário abrir o caixa para operar o sistema.");
                fazerLogout()
            }
        } else {
            document.getElementById('menu-caixa-valor').textContent = `R$ ${caixa.valor_atual.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
            localStorage.setItem('cod_caixa', caixa.cod_caixa);
        }
    } catch (error) {
        console.error("Erro ao verificar caixa:", error);
    }
}

document.querySelector('.btn-fechar-caixa').addEventListener('click', async () => {
    const cod_caixa = localStorage.getItem('cod_caixa');
    const valorFechamento = localStorage.getItem('valorcaixa');

    const fecharCaixaOption = confirm("Deseja realmente fechar o caixa?");

    if (fecharCaixaOption) {
        if (valorFechamento !== null) {
            const response = await fetch("http://127.0.0.1:8000/caixa/fechar-caixa", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    cod_caixa: parseInt(cod_caixa),
                    valor_fechamento: parseFloat(valorFechamento.replace(',', '.'))
                })
            });

            if (response.ok) {
                fazerLogout()
                location.href = 'login.html'
            }
        }
    } else {
        return
    }
});


document.addEventListener('DOMContentLoaded', carregarCategorias);
exibirData();
carregarProdutos();
atualizarTotais();
