function mostrarToast(mensagem, tipo = 'sucesso') {
    const toast = document.createElement('div');
    toast.className = `toast toast--${tipo}`;
    toast.setAttribute('role', 'status');
    toast.textContent = mensagem;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast--saindo');
        setTimeout(() => toast.remove(), 200);
    }, 2500);
}
