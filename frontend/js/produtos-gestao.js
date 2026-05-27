const BASE_URL = "http://127.0.0.1:8000";

// Carrega as configurações de menu igual da página com o dash
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



// Funcionamanto da edição
async function carregarCategorias() {
    const nav = document.getElementById('categorias-nav');
    const selectCategoria = document.getElementById('categoria_produto');
    
    try {
        const response = await fetch(`${BASE_URL}/produtos/categorias`);
        const categorias = await response.json();

        if (selectCategoria) {
            selectCategoria.innerHTML = '<option value="">Selecione...</option>';
        }

        categorias.forEach(cat => {
            const button = document.createElement('button');
            button.className = 'categoria-card';
            button.dataset.category = cat.cod_categoria;
            button.innerHTML = `
                <div class="categoria-card__icone">
                    <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" /></svg>
                </div>
                <span class="categoria-card__label">${cat.categoria_produto}</span>
                <span class="categoria-card__count">${cat.total_produtos} itens</span>
            `;
            button.addEventListener('click', () => {
                selecionarCategoria(button, cat.cod_categoria);
            });
            nav.appendChild(button);

            if (selectCategoria) {
                const option = document.createElement('option');
                option.value = cat.cod_categoria;
                option.textContent = cat.categoria_produto;
                selectCategoria.appendChild(option);
            }
        });

        const totalGeral = categorias.reduce((acc, c) => acc + parseInt(c.total_produtos), 0);
        document.getElementById('total-count').textContent = `${totalGeral} itens`;

    } catch (error) {
        console.error("Erro nas categorias:", error);
    }
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

function fazerLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario_nome');
    localStorage.removeItem('usuario_cargo');
    localStorage.removeItem('cod_colaborador');
    localStorage.removeItem('loja_id');
    localStorage.removeItem('loja_nome');
    window.location.href = "login.html";
}

async function carregarFragranciasForm() {
    const container = document.getElementById('lista-fragrancias');
    if (!container) return;

    try {
        const response = await fetch(`${BASE_URL}/produtos/fragrancias`);
        const fragrancias = await response.json();

        container.innerHTML = '';
        fragrancias.forEach(f => {
            const span = document.createElement('span');
            span.className = 'fragrancia-option';
            span.dataset.id = f.cod_fragrancia;
            span.textContent = f.nome_fragrancia;
            span.onclick = () => span.classList.toggle('selected');
            container.appendChild(span);
        });
    } catch (error) {
        console.error("Erro ao carregar fragrâncias:", error);
    }
}

function selecionarCategoria(elemento, id) {
    document.querySelectorAll('.categoria-card').forEach(btn => btn.classList.remove('active'));
    elemento.classList.add('active');
    carregarProdutosTabela(id === 'todas' ? null : id);
}

async function carregarProdutosTabela(categoriaId = null) {
    const tabelaBody = document.getElementById('tabela-produtos-body');
    if (!tabelaBody) return;

    try {
        let url = `${BASE_URL}/produtos/`;
        if (categoriaId) url = `${BASE_URL}/produtos/categoria/${categoriaId}`;

        const response = await fetch(url);
        const produtos = await response.json();
        
        tabelaBody.innerHTML = '';

        produtos.forEach(prod => {
            const tr = document.createElement('tr');
            const statusClass = prod.ativo ? 'tag--sucesso' : 'tag--cuidado';
            const statusText = prod.ativo ? 'Ativo' : 'Inativo';

            tr.innerHTML = `
                <td>
                    <div class="produto-info-cell">
                        <img src="${BASE_URL}${prod.url_imagem}" alt="${prod.nome_produto}" class="produto-img-mini">
                        <span>${prod.nome_produto}</span>
                    </div>
                </td>
                <td>${prod.marca}</td>
                <td><span class="tag">${prod.categoria_produto || 'Geral'}</span></td>
                <td>${prod.preco_unitario.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
                <td><span class="tag ${statusClass}">${statusText}</span></td>
                <td style="text-align: right;">
                    <button class="btn-icon" onclick="prepararEdicao(${prod.cod_produto})" title="Editar">
                        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7M18.5 2.5a2.121 2.121 0 113 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                    </button>
                </td>
            `;
            tabelaBody.appendChild(tr);
        });
    } catch (error) {
        console.error("Erro ao carregar produtos:", error);
    }
}

async function salvarProduto(event) {
    if (event) event.preventDefault();
    
    const cod_produto = document.getElementById('cod_produto').value;
    const mensagemConfirma = cod_produto ? "Deseja salvar as alterações neste produto?" : "Deseja cadastrar este novo produto?";
    
    if (!confirm(mensagemConfirma)) return;


    const fragranciasSelecionadas = Array.from(document.querySelectorAll('.fragrancia-option.selected'))
        .map(el => parseInt(el.dataset.id));
    const arquivoImagem = document.getElementById('imagem_produto').files[0];

    const formData = new FormData();
    formData.append('cod_produto', cod_produto);
    formData.append('nome_produto', document.getElementById('nome_produto').value);
    formData.append('marca', document.getElementById('marca_produto').value);
    formData.append('descricao', document.getElementById('descricao_produto').value);
    formData.append('preco_unitario', document.getElementById('preco_produto').value);
    formData.append('cod_categoria', document.getElementById('categoria_produto').value);
    formData.append('ativo', document.getElementById('ativo').checked);
    formData.append('fragrancias', JSON.stringify(fragranciasSelecionadas));

    if (cod_produto) {
        formData.append('url_imagem_atual', document.getElementById('url_imagem_atual').value);
    }

    if (arquivoImagem) {
        formData.append('imagem', arquivoImagem);
    }
    
    // console.log(formData)
    // confirm(formData)

    try {
        const url = cod_produto 
            ? `${BASE_URL}/produtos/atualizar/${cod_produto}` 
            : `${BASE_URL}/produtos/novo_produto`;
            
        const method = cod_produto ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            body: formData // Sem headers Content-Type, o browser define como multipart/form-data
        });

        if (response.ok) {
            alert(cod_produto ? "Produto atualizado!" : "Produto cadastrado!");
            limparFormulario();
            carregarProdutosTabela();
            carregarCategorias();
        }
    } catch (error) {
        console.error("Erro ao salvar:", error);
        alert("Erro ao salvar produto");
    }
}

function limparFormulario() {
    document.getElementById('form-produto').reset();
    document.getElementById('cod_produto').value = '';
    document.getElementById('url_imagem_atual').value = '';
    document.getElementById('imagem_produto').value = '';
    document.getElementById('preview-imagem').src = `${BASE_URL}/static/products/padrao.png`;
    document.getElementById('titulo-formulario').textContent = 'Novo produto';
    document.querySelectorAll('.fragrancia-option').forEach(el => el.classList.remove('selected'));
}

document.getElementById('btn-limpar-form').addEventListener('click', async () => {
    if (confirm("Deseja realmente limpar o formulário?")) {
        limparFormulario();
    }
})

document.getElementById('form-produto').addEventListener('submit', salvarProduto);

async function prepararEdicao(id) {
    try {
        const response = await fetch(`${BASE_URL}/produtos/${id}`);
        const prod = await response.json();

        document.getElementById('cod_produto').value = prod.id || prod.cod_produto;
        document.getElementById('nome_produto').value = prod.nome || prod.nome_produto;
        document.getElementById('marca_produto').value = prod.marca;
        document.getElementById('preco_produto').value = prod.preco || prod.preco_unitario;
        document.getElementById('descricao_produto').value = prod.descricao || '';
        document.getElementById('ativo').checked = prod.ativo;
        
        if (prod.cod_categoria) {
            document.getElementById('categoria_produto').value = prod.cod_categoria;
        }

        if (prod.url_imagem) {
            document.getElementById('preview-imagem').src = `${BASE_URL}${prod.url_imagem}`;
            document.getElementById('url_imagem_atual').value = prod.url_imagem;
        }

        document.querySelectorAll('.fragrancia-option').forEach(el => {
            const fragId = parseInt(el.dataset.id);
            const possui = prod.fragrancias.some(f => f.cod_fragrancia === fragId);
            el.classList.toggle('selected', possui);
        });

        document.getElementById('titulo-formulario').textContent = 'Editando produto';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
        console.error("Erro ao carregar para edição:", error);
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
    carregarCategorias();
    carregarFragranciasForm();
    carregarProdutosTabela();
    limparFormulario();

    document.getElementById('imagem_produto').addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => document.getElementById('preview-imagem').src = e.target.result;
            reader.readAsDataURL(file);
        }
    });

    const btnTodas = document.querySelector('[data-category="todas"]');
    if (btnTodas) {
        btnTodas.addEventListener('click', () => selecionarCategoria(btnTodas, 'todas'));
    }
});
