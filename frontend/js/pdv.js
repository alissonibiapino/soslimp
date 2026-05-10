// Variaveis
let carrinho = [];

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

        console.log(categorias)

        categorias.forEach(cat => {
            const button = document.createElement('button');
            button.className = 'categoria-card';
            button.dataset.category = cat.id;

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
                console.log(`Filtrando categoria: ${cat.categoria_produto}, com o ID ${cat.cod_categoria}`)
            })

            nav.appendChild(button);
        });
    } catch (error) {
        console.error("Erro nas categorias:", error)
    }
}

// Produtos
async function carregarProduto() {
    const produtos_grid = document.getElementById('produtos-grid')

    try {
        const response = await fetch("http://127.0.0.1:8000/produtos/categoria/2");
        const produtos = await response.json()

        console.log(produtos)

        produtos.forEach(prod => {
            console.log(prod.id)

            const article = document.createElement('article');
            article.className = 'produto-card';
            article.dataset.id = prod.id;

            article.innerHTML = `
                <div class="produto-card__imagem_box">
                    <img alt="${prod.nome}" class="produto-card__imagem" />
                </div>
                <div class="produto-card__corpo">
                    <h3 class="produto-card__nome">${prod.nome}</h3>
                    <span class="produto-card__preco">${prod.preco.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span>
                </div>
            `;

            article.addEventListener('click', () => adicionarAoCarrinho(prod));
            produtos_grid.appendChild(article)

        });

    } catch (error) {
        console.error("Erro nas categorias:", error)
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
                <button class="qty-btn" onclick="alterarQuantidade(${item.id}, -1)">-</button>
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
}

function adicionarAoCarrinho(produto) {
    const itemExistente = carrinho.find(item => item.id === produto.id);

    if (itemExistente) {
        itemExistente.quantidade += 1;
    } else {
        carrinho.push({
            id: produto.id,
            nome: produto.nome,
            preco: produto.preco,
            marca: produto.marca || 'SOSLimp',
            quantidade: 1
        });
    }
    atualizarCarrinhoHTML();
}


function alterarQuantidade(id, delta) {
    const item = carrinho.find(item => item.id === id);
    if (!item) return;

    item.quantidade += delta;

    if (item.quantidade <= 0) {
        carrinho = carrinho.filter(i => i.id !== id);
    }

    atualizarCarrinhoHTML();
}



document.addEventListener('DOMContentLoaded', carregarCategorias);
exibirData();
carregarProduto();
