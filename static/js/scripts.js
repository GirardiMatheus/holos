document.addEventListener('DOMContentLoaded', () => {
    carregarExames(); 
    document.getElementById('form-cadastrar').addEventListener('submit', cadastrarExame);
    document.getElementById('form-orcamento').addEventListener('submit', gerarOrcamento);
});

let todosExames = []; 
let examesSelecionados = new Set(); 

function openTab(tabName) {
    const tabcontents = document.getElementsByClassName('tabcontent');
    for (let i = 0; i < tabcontents.length; i++) {
        tabcontents[i].style.display = 'none';
    }
    document.getElementById(tabName).style.display = 'block';
}

function carregarExames() {
    fetch('/exames')
        .then(response => response.json())
        .then(data => {
            todosExames = data; 
            atualizarListaExames(data); 
            atualizarListaExamesOrcamento(data); 
        });
}

function atualizarListaExames(exames) {
    const listaExames = document.getElementById('lista-exames');
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

function filtrarExames() {
    const termo = document.getElementById('pesquisa-exames').value.toLowerCase().substring(0, 3); 
    const examesFiltrados = todosExames.filter(exame => exame.nome.toLowerCase().startsWith(termo));
    atualizarListaExames(examesFiltrados); 
}

function filtrarExamesOrcamento() {
    const termo = document.getElementById('pesquisa-orcamento').value.toLowerCase().substring(0, 3); 
    const examesFiltrados = todosExames.filter(exame => exame.nome.toLowerCase().startsWith(termo));

    atualizarListaExamesOrcamento(examesFiltrados);

    examesSelecionados.forEach(nome => {
        const checkbox = document.querySelector(`input[name="exames"][value="${nome}"]`);
        if (checkbox) {
            checkbox.checked = true;
        }
    });
}

function atualizarListaExamesOrcamento(exames) {
    const listaExamesOrcamento = document.getElementById('lista-exames-orcamento');
    listaExamesOrcamento.innerHTML = '';

    exames.forEach(exame => {
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.name = 'exames';
        checkbox.value = exame.nome;
        checkbox.dataset.valor = exame.valor;

        if (examesSelecionados.has(exame.nome)) {
            checkbox.checked = true;
        }

        checkbox.addEventListener('change', (event) => {
            if (event.target.checked) {
                examesSelecionados.add(exame.nome);
            } else {
                examesSelecionados.delete(exame.nome);
            }
        });

        const label = document.createElement('label');
        label.textContent = `${exame.nome} - R$ ${exame.valor}`;
        label.appendChild(checkbox);

        listaExamesOrcamento.appendChild(label);
        listaExamesOrcamento.appendChild(document.createElement('br'));
    });
}

function cadastrarExame(event) {
    event.preventDefault();
    const nome = document.getElementById('nome').value;
    const valor = document.getElementById('valor').value;

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
        limparCamposCadastro(); 
    });
}

function limparCamposCadastro() {
    document.getElementById('nome').value = '';
    document.getElementById('valor').value = '';
}

function editarExame(nome, valor) {
    const novoNome = prompt("Editar nome do exame:", nome);
    const novoValor = prompt("Editar valor do exame:", valor);

    if (novoNome && novoValor) {
        fetch('/editar_exame', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ nomeAntigo: nome, nomeNovo: novoNome, valor: novoValor }),
        })
        .then(response => response.json())
        .then(data => {
            mostrarMensagem('Exame editado com sucesso!');
            carregarExames(); 
        });
    }
}

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
        });
    }
}

function gerarOrcamento(event) {
    event.preventDefault();
    const cliente = document.getElementById('cliente').value;
    const cpf = document.getElementById('cpf').value;
    const examesSelecionadosArray = Array.from(document.querySelectorAll('input[name="exames"]:checked'))
        .map(checkbox => ({ nome: checkbox.value, valor: checkbox.dataset.valor }));

    fetch('/gerar_orcamento', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cliente, cpf, exames: examesSelecionadosArray }),
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `orcamento_${cliente}.pdf`;
        a.click();
        limparCamposOrcamento(); 
    });
}

function limparCamposOrcamento() {
    document.getElementById('cliente').value = '';
    document.getElementById('cpf').value = '';
    const checkboxes = document.querySelectorAll('input[name="exames"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    examesSelecionados.clear(); 
}

function mostrarMensagem(mensagem, tipo = 'success') {
    const mensagemDiv = document.createElement('div');
    mensagemDiv.className = 'mensagem';
    mensagemDiv.textContent = mensagem;
    mensagemDiv.style.backgroundColor = tipo === 'error' ? '#950606' : '#4CAF50'; 
    document.body.appendChild(mensagemDiv);
    setTimeout(() => mensagemDiv.remove(), 3000);
}

function exportarCSV() {
    fetch('/exportar_csv')
        .then(response => response.blob())
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
            mostrarMensagem('Erro ao exportar CSV.', 'error');
        });
}

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
            mostrarMensagem('Erro ao importar CSV.', 'error');
        }
    })
    .catch(error => {
        console.error('Erro ao importar CSV:', error);
        mostrarMensagem('Erro ao importar CSV.', 'error');
    });
}