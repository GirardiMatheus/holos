function mostrarMensagem(mensagem, tipo) {
  const mensagemDiv = document.createElement('div');
  mensagemDiv.className = 'mensagem';
  mensagemDiv.textContent = mensagem;
  mensagemDiv.style.backgroundColor = tipo === 'error' ? '#950606' : '#4CAF50';
  document.body.appendChild(mensagemDiv);
  setTimeout(() => mensagemDiv.remove(), 3000);
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
