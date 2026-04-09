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

exibirData();

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

document.addEventListener('DOMContentLoaded', carregarCategorias);
