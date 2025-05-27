// Variáveis globais
let todosExames = [];
let examesSelecionados = new Set();
let examesCarregados = false;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Configura os event listeners das abas
    const tablinks = document.querySelectorAll('.tablink');
    tablinks.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            openTab(tabName);
        });
    });

    // Ativa a primeira aba por padrão
    openTab('exames');

    // Configura os event listeners dos formulários
    document.getElementById('form-cadastrar')?.addEventListener('submit', cadastrarExame);
    document.getElementById('form-orcamento')?.addEventListener('submit', gerarOrcamento);
});

// Função para alternar entre abas
function openTab(tabName) {
    // Esconde todos os conteúdos das abas
    const tabcontents = document.querySelectorAll('.tabcontent');
    tabcontents.forEach(tab => {
        tab.classList.remove('active-tab');
    });

    // Remove a classe 'active' de todas as abas
    const tablinks = document.querySelectorAll('.tablink');
    tablinks.forEach(tab => {
        tab.classList.remove('active');
    });

    // Mostra a aba atual e ativa o botão correspondente
    document.getElementById(tabName)?.classList.add('active-tab');
    document.querySelector(`.tablink[data-tab="${tabName}"]`)?.classList.add('active');

    // Carrega os exames se necessário
    if ((tabName === 'exames' || tabName === 'orcamentos') && !examesCarregados) {
        carregarExames();
        examesCarregados = true;
    }
}

// Função para carregar os exames
function carregarExames() {
    fetch('/exames')
        .then(response => {
            if (!response.ok) throw new Error('Erro na rede');
            return response.json();
        })
        .then(data => {
            todosExames = data;
            atualizarListaExames(data);
            atualizarListaExamesOrcamento(data);
        })
        .catch(error => {
            console.error('Erro ao carregar exames:', error);
            mostrarMensagem('Erro ao carregar exames', 'error');
        });
}

// Função para atualizar a lista de exames
function atualizarListaExames(exames) {
    const listaExames = document.getElementById('lista-exames');
    if (!listaExames) return;

    listaExames.innerHTML = '';

    exames.forEach(exame => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <h3>${exame.nome}</h3>
            <p>R$ ${exame.valor}</p>
            <button onclick="editarExame('${exame.nome}', '${exame.valor}')">Editar</button>
            <button onclick="excluirExame('${exame.nome}')">Excluir</button>
        `;
        listaExames.appendChild(card);
    });
}

// Função para filtrar exames
function filtrarExames() {
    const termo = document.getElementById('pesquisa-exames')?.value.toLowerCase().substring(0, 3) || '';
    const examesFiltrados = todosExames.filter(exame => 
        exame.nome.toLowerCase().startsWith(termo)
    );
    atualizarListaExames(examesFiltrados);
}

// Função para atualizar a lista de exames no orçamento
function atualizarListaExamesOrcamento(exames) {
    const listaExamesOrcamento = document.getElementById('lista-exames-orcamento');
    if (!listaExamesOrcamento) return;

    listaExamesOrcamento.innerHTML = '';

    if (exames.length === 0) {
        listaExamesOrcamento.innerHTML = '<p class="sem-exames">Nenhum exame encontrado</p>';
        return;
    }

    exames.forEach(exame => {
        const div = document.createElement('div');
        div.className = 'exame-item';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.name = 'exames';
        checkbox.value = exame.nome;
        checkbox.dataset.valor = exame.valor;
        checkbox.id = `exame-${exame.nome.replace(/\s+/g, '-')}`;
        
        if (examesSelecionados.has(exame.nome)) {
            checkbox.checked = true;
        }

        checkbox.addEventListener('change', function() {
            if (this.checked) {
                examesSelecionados.add(exame.nome);
            } else {
                examesSelecionados.delete(exame.nome);
            }
        });

        const label = document.createElement('label');
        label.htmlFor = checkbox.id;
        label.textContent = `${exame.nome} - R$ ${parseFloat(exame.valor).toFixed(2)}`;

        div.appendChild(checkbox);
        div.appendChild(label);
        listaExamesOrcamento.appendChild(div);
    });
}

// Função para filtrar exames no orçamento
function filtrarExamesOrcamento() {
    const termo = document.getElementById('pesquisa-orcamento')?.value.toLowerCase().substring(0, 3) || '';
    const examesFiltrados = todosExames.filter(exame => 
        exame.nome.toLowerCase().startsWith(termo)
    );
    atualizarListaExamesOrcamento(examesFiltrados);
}

// Função para cadastrar novo exame
function cadastrarExame(event) {
    event.preventDefault();
    const nome = document.getElementById('nome')?.value;
    const valor = document.getElementById('valor')?.value;

    if (!nome || !valor) {
        mostrarMensagem('Preencha todos os campos', 'error');
        return;
    }

    fetch('/cadastrar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nome, valor }),
    })
    .then(response => response.json())
    .then(data => {
        mostrarMensagem('Exame cadastrado com sucesso!');
        carregarExames();
        document.getElementById('form-cadastrar')?.reset();
    })
    .catch(error => {
        console.error('Erro ao cadastrar exame:', error);
        mostrarMensagem('Erro ao cadastrar exame', 'error');
    });
}

// Função para editar exame
function editarExame(nome, valor) {
    const novoNome = prompt("Editar nome do exame:", nome);
    const novoValor = prompt("Editar valor do exame:", valor);

    if (novoNome && novoValor) {
        fetch('/editar_exame', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                nomeAntigo: nome, 
                nomeNovo: novoNome, 
                valor: novoValor 
            }),
        })
        .then(response => response.json())
        .then(data => {
            mostrarMensagem('Exame editado com sucesso!');
            carregarExames();
        })
        .catch(error => {
            console.error('Erro ao editar exame:', error);
            mostrarMensagem('Erro ao editar exame', 'error');
        });
    }
}

// Função para excluir exame
function excluirExame(nome) {
    if (confirm(`Tem certeza que deseja excluir o exame "${nome}"?`)) {
        fetch('/excluir_exame', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ nome }),
        })
        .then(response => response.json())
        .then(data => {
            mostrarMensagem('Exame excluído com sucesso!');
            carregarExames();
        })
        .catch(error => {
            console.error('Erro ao excluir exame:', error);
            mostrarMensagem('Erro ao excluir exame', 'error');
        });
    }
}

// Função para gerar orçamento
function gerarOrcamento(event) {
    event.preventDefault();
    const cliente = document.getElementById('cliente')?.value;
    const cpf = document.getElementById('cpf')?.value;

    if (!cliente || !cpf || examesSelecionados.size === 0) {
        mostrarMensagem('Preencha todos os campos e selecione pelo menos um exame', 'error');
        return;
    }

    const examesSelecionadosArray = Array.from(examesSelecionados).map(nome => {
        const exame = todosExames.find(e => e.nome === nome);
        return { nome, valor: exame?.valor || '0' };
    });

    fetch('/gerar_orcamento', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            cliente, 
            cpf, 
            exames: examesSelecionadosArray 
        }),
    })
    .then(response => {
        if (!response.ok) throw new Error('Erro ao gerar orçamento');
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `orcamento_${cliente}.pdf`;
        a.click();
        mostrarMensagem('Orçamento gerado com sucesso!');
        document.getElementById('form-orcamento')?.reset();
        examesSelecionados.clear();
    })
    .catch(error => {
        console.error('Erro ao gerar orçamento:', error);
        mostrarMensagem('Erro ao gerar orçamento', 'error');
    });
}

// Função para exportar CSV
function exportarCSV() {
    fetch('/exportar_csv')
        .then(response => {
            if (!response.ok) throw new Error('Erro ao exportar CSV');
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'exames.csv';
            a.click();
            mostrarMensagem('CSV exportado com sucesso!');
        })
        .catch(error => {
            console.error('Erro ao exportar CSV:', error);
            mostrarMensagem('Erro ao exportar CSV', 'error');
        });
}

// Função para importar CSV
function importarCSV(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    fetch('/importar_csv', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            mostrarMensagem('CSV importado com sucesso!');
            carregarExames();
        } else {
            throw new Error(data.message || 'Erro ao importar CSV');
        }
    })
    .catch(error => {
        console.error('Erro ao importar CSV:', error);
        mostrarMensagem(error.message || 'Erro ao importar CSV', 'error');
    });
}

// Função para mostrar mensagens
function mostrarMensagem(mensagem, tipo = 'success') {
    // Remove mensagens existentes
    const mensagensExistentes = document.querySelectorAll('.mensagem');
    mensagensExistentes.forEach(msg => msg.remove());
    
    const mensagemDiv = document.createElement('div');
    mensagemDiv.className = `mensagem ${tipo}`;
    
    // Adiciona ícone conforme o tipo
    const icone = document.createElement('i');
    icone.className = tipo === 'error' ? 'fas fa-exclamation-circle' : 'fas fa-check-circle';
    mensagemDiv.appendChild(icone);
    
    // Adiciona texto
    const texto = document.createElement('span');
    texto.textContent = mensagem;
    mensagemDiv.appendChild(texto);
    
    document.body.appendChild(mensagemDiv);
    
    // Remove a mensagem após 3 segundos
    setTimeout(() => {
        mensagemDiv.style.animation = 'fadeOut 0.5s ease';
        setTimeout(() => mensagemDiv.remove(), 500);
    }, 3000);
}