// Variaveis
const BASE_URL = "http://127.0.0.1:8000";
let carrinho = [];
let metodoPagamento = 1;

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

function atualizarRelogio() {
    const agora = new Date();
    document.getElementById('menu-hora').textContent = agora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

// Categorias
async function carregarCategorias() {
    const nav = document.getElementById('categorias-nav')

    try {
        const response = await fetch(`${BASE_URL}/produtos/categorias`);
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
        let url = `${BASE_URL}/produtos`;

        if (categoriaId) {
            url = `${BASE_URL}/produtos/categoria/${categoriaId}`;
        }

        const response = await fetch(url);
        const produtos = await response.json()

        produtos.forEach(prod => {
            const article = document.createElement('article');
            article.className = 'produto-card';
            
            if (!prod.ativo) {
                article.classList.add('produto-card--inativo');
            }

            article.innerHTML = `
                <div class="produto-card__imagem_box">
                    <img class="produto-card__imagem" src="${BASE_URL}${prod.url_imagem}" alt="${prod.nome_produto}"/>
                </div>
                <div class="produto-card__corpo">
                    <h3 class="produto-card__nome">${prod.nome_produto}</h3>
                    <strong class="produto-card__marca">${prod.marca}</strong>
                    <div class="produto-card__fragrancias">
                        ${prod.fragrancias && prod.fragrancias.length > 0
                            ? prod.fragrancias.map(f => {
                                const slug = f.nome_fragrancia.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, '-');
                                return `<span class="tag tag--fragrancia tag--${slug}">${f.nome_fragrancia}</span>`;
                            }).join(' ')
                            : '<span class="tag tag--fragrancia tag--neutro">Padrão</span>'
                        }
                    </div>
                    <span class="produto-card__preco">${prod.preco_unitario.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span>
                </div>
            `;

            // Adiciona o evento de clique apenas se o produto estiver ativo
            if (prod.ativo) {
                article.addEventListener('click', () => adicionarAoCarrinho(prod));
            }
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
        li.dataset.id = item.cod_produto;

        const fragranciasHTML = item.fragrancias.map(f => {
            const slug = f.nome_fragrancia.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, '-');
            const activeClass = item.cod_fragrancia === f.cod_fragrancia ? 'active' : '';
            return `<span class="tag tag--fragrancia tag--${slug} ${activeClass}" 
                          onclick="selecionarFragrancia(${item.cod_produto}, ${f.cod_fragrancia})">${f.nome_fragrancia}</span>`;
        }).join('');

        li.innerHTML = `
            <div class="venda-item__qty">
                <button class="qty-btn" onclick="alterarQuantidade(${item.cod_produto}, -1)">-</button>
                <span class="qty-value">${item.quantidade}</span>
                <button class="qty-btn" onclick="alterarQuantidade(${item.cod_produto}, 1)">+</button>
            </div>
            <div class="venda-item__info">
                <span class="venda-item__nome">${item.nome}</span>
                <strong class="venda-item__marca">${item.marca}</strong>
                <div class="venda-item__tags">
                    ${fragranciasHTML}
                </div>
            </div>
            <span class="venda-item__preco">R$ ${(item.preco * item.quantidade).toFixed(2).replace('.', ',')}</span>
        `;
        listaVenda.appendChild(li);
    });
    atualizarTotais();
}

// Função para trocar a fragrância do item no carrinho
function selecionarFragrancia(codProduto, codFragrancia) {
    const item = carrinho.find(i => i.cod_produto === codProduto);
    if (item) {
        item.cod_fragrancia = codFragrancia;
        atualizarCarrinhoHTML();
    }
}

function adicionarAoCarrinho(produto, isRecomendacao = false) {
    const itemExistente = carrinho.find(item => item.cod_produto === produto.cod_produto);

    if (itemExistente) {
        itemExistente.quantidade += 1;
    } else {
        carrinho.push({
            cod_produto: produto.cod_produto,
            nome: produto.nome_produto,
            preco: produto.preco_unitario,
            marca: produto.marca || 'SOSLimp',
            quantidade: 1,
            cod_fragrancia: (produto.fragrancias && produto.fragrancias.length > 0) ? produto.fragrancias[0].cod_fragrancia : 18,
            fragrancias: produto.fragrancias || [],
            is_recomendacao: isRecomendacao
        });
    }
    atualizarCarrinhoHTML();
    buscarRecomendacoes()
    atualizarTotais();
}

function alterarQuantidade(id, delta) {
    const item = carrinho.find(item => Number(item.cod_produto) === Number(id));
    if (!item) return;

    item.quantidade += delta;

    if (item.quantidade <= 0) {
        carrinho = carrinho.filter(i => Number(i.cod_produto) !== Number(id));
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

    const cods = carrinho.map(produto => produto.cod_produto)

    try {
        const response = await fetch(`${BASE_URL}/produtos/produtos_recomendados`, {
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

        article.addEventListener('click', () => adicionarAoCarrinho(prod, true)); // Passa 'true' para indicar que é uma recomendação
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

    const dinheiroCliente = parseFloat(document.getElementById('dinheiro-recebido').value) || 0;
    const btnRegistrar = document.getElementById('btn-registrar-venda');
    const btnLimpar = document.getElementById('btn-limpar-venda');

    let isVendaValida = carrinho.length > 0 && metodoPagamento;
    if (metodoPagamento == 4 && dinheiroCliente < total) {
        isVendaValida = false;
    }

    btnRegistrar.disabled = !isVendaValida;
    btnLimpar.disabled = (carrinho.length === 0);

    if (metodoPagamento == 4) calcularTroco();
}

function calcularTroco() {
    const totalTexto = document.getElementById('total').textContent;
    const totalValue = parseFloat(totalTexto.replace('R$', '').replace('.', '').replace(',', '.')) || 0;
    const dinheiroCliente = parseFloat(document.getElementById('dinheiro-recebido').value) || 0;

    const trocoCliente = Math.max(0, dinheiroCliente - totalValue);
    document.getElementById('change-amount').textContent = trocoCliente.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    
    const btnRegistrar = document.getElementById('btn-registrar-venda');
    btnRegistrar.disabled = (carrinho.length === 0 || (metodoPagamento == 4 && dinheiroCliente < totalValue));
}

document.querySelectorAll('.metodo-pagamento').forEach(botao => {
    botao.addEventListener('click', () => {
        document.querySelectorAll('.metodo-pagamento').forEach(b => {
            b.classList.remove('metodo-pagamento--ativo');
        });

        botao.classList.add('metodo-pagamento--ativo');

        metodoPagamento = botao.dataset.method;

        const cashDetails = document.querySelector('.troco-pagamento-detalhes');
        if (metodoPagamento == 4) {
            cashDetails.style.display = 'block';
            document.getElementById('dinheiro-recebido').focus();
        } else {
            cashDetails.style.display = 'none';
            document.getElementById('dinheiro-recebido').value = '';
        }

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

document.getElementById('dinheiro-recebido').addEventListener('input', calcularTroco);

// document.getElementById('btn-registrar-venda').addEventListener('click', () => {
//     if (confirm("Deseja confirmar a venda?")) {
//         realizarVenda()
//     }
// });


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

// Finalizar compra
document.getElementById('btn-registrar-venda').addEventListener('click', async () => {
    const cod_caixa = localStorage.getItem('cod_caixa');
    const cod_colaborador = localStorage.getItem('cod_colaborador');
    const cod_loja = localStorage.getItem('loja_id');
    
    const valorRecebido = metodoPagamento == 4 ? parseFloat(document.getElementById('dinheiro-recebido').value) : 0;

    try {
        const response = await fetch(`${BASE_URL}/vendas/novo_pedido`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                cod_caixa: parseInt(cod_caixa),
                cod_colaborador: parseInt(cod_colaborador),
                cod_forma_pag: parseInt(metodoPagamento),
                cod_loja: parseInt(cod_loja),
                produtos: carrinho,
                valor_recebido: valorRecebido
            })
        });
        if (response.ok) {
            alert('Venda efetuada com sucesso!');
            
            // Limpar PDV após a venda
            carrinho = [];
            document.getElementById('dinheiro-recebido').value = '';
            atualizarCarrinhoHTML();
            atualizarTotais();
            buscarRecomendacoes();
            
            // Atualizar o valor do caixa no menu superior
            verificarStatusCaixa();
        }
    } catch (error) {
        alert('Venda não efetuada')
        console.error("Erro ao efetuar pedido:", error)
    }
})


document.addEventListener('DOMContentLoaded', carregarCategorias);
exibirData();
atualizarRelogio();
setInterval(atualizarRelogio, 60000);
carregarProdutos();
atualizarTotais();
