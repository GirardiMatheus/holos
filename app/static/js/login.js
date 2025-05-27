function mostrarMensagem(mensagem, tipo = 'success') {
    const mensagensExistentes = document.querySelectorAll('.mensagem');
    mensagensExistentes.forEach(msg => msg.remove());
    
    const mensagemDiv = document.createElement('div');
    mensagemDiv.className = `mensagem ${tipo}`;
    
    const icone = document.createElement('i');
    icone.className = tipo === 'error' ? 'fas fa-exclamation-circle' : 'fas fa-check-circle';
    mensagemDiv.appendChild(icone);
    
    const texto = document.createElement('span');
    texto.textContent = mensagem;
    mensagemDiv.appendChild(texto);
    
    document.body.appendChild(mensagemDiv);
    
    setTimeout(() => {
        mensagemDiv.style.animation = 'fadeOut 0.5s ease';
        setTimeout(() => mensagemDiv.remove(), 500);
    }, 3000);
}

document.getElementById('form-login').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(this);

    fetch('/login', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.ok ? response.json() : Promise.reject())
    .then(data => {
        mostrarMensagem(data.message, data.status === 'success' ? 'success' : 'error');
        if (data.status === 'success') {
            setTimeout(() => window.location.href = '/', 1000);
        }
    })
    .catch(() => mostrarMensagem('Erro ao tentar fazer login', 'error'));
});
