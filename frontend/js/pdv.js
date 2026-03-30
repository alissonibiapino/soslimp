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