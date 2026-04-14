// core/static/js/maquinas.js

window.maquinaAtivaId = null;

function atualizarDetalhes(elemento, nome, modelo, horimetro, fazenda, identificacao, pk_banco) {
    window.maquinaAtivaId = pk_banco;
    
    // Salva no navegador qual máquina está aberta
    localStorage.setItem('ultimaMaquinaSelecionada', pk_banco);

    // Gerencia o destaque visual na lista
    document.querySelectorAll('.machine-item').forEach(item => {
        item.classList.remove('active');
    });
    elemento.classList.add('active');

    // Atualiza os dados no painel da direita
    document.getElementById('view-titulo').innerText = nome + " " + modelo;
    document.getElementById('view-horimetro').innerText = horimetro;
    document.getElementById('view-fazenda').innerText = fazenda;
    document.getElementById('view-id').innerText = identificacao;

    // --- ATUALIZA OS LINKS DE EDITAR E EXCLUIR ---
    const btnEditar = document.getElementById('link-editar-maquina');
    const btnDeletar = document.getElementById('link-deletar-maquina');

    if (pk_banco && btnEditar && btnDeletar) {
        btnEditar.href = `/maquinas/editar/${pk_banco}/`;
        btnDeletar.href = `/maquinas/deletar/${pk_banco}/`;
        
        // Garante que os botões apareçam
        btnEditar.style.display = 'flex';
        btnDeletar.style.display = 'flex';
    }

    renderizarTarefasVisuais(pk_banco);
}

function renderizarTarefasVisuais(maquinaId) {
    const container = document.getElementById('container-tarefas');
    const dadosOcultos = document.getElementById('tarefas-data-' + maquinaId);
    
    if (!container) return;
    container.innerHTML = ''; 

    if (dadosOcultos && dadosOcultos.children.length > 0) {
        Array.from(dadosOcultos.children).forEach(span => {
            const idTarefa = span.getAttribute('data-id');
            const concluida = span.getAttribute('data-concluida') === 'true';
            const texto = span.innerText;

            container.innerHTML += `
                <div class="task-item" style="display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 10px; background: #f9f9f9; padding: 10px; border-radius: 8px; border-left: 4px solid ${concluida ? '#888' : '#4b6630'};">
                    <div style="display: flex; align-items: center; gap: 10px; flex: 1;">
                        <input type="checkbox" ${concluida ? 'checked' : ''} onchange="toggleTarefa(${idTarefa})" style="cursor: pointer; transform: scale(1.2);">
                        <span style="${concluida ? 'text-decoration: line-through; color: #888;' : 'color: #333; font-weight: 500;'}">
                            ${texto}
                        </span>
                    </div>
                    <button onclick="deletarTarefa(${idTarefa})" style="background: none; border: none; color: #e74c3c; cursor: pointer; padding: 5px;">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>`;
        });
    } else {
        container.innerHTML = '<p style="color: #999; font-size: 0.85rem; text-align: center; padding: 20px;">Nenhuma observação registrada.</p>';
    }
}

async function salvarTarefa() {
    const input = document.getElementById('nova-tarefa-input');
    let desc = input.value.trim();
    if (!desc || !window.maquinaAtivaId) return;

    desc = desc.charAt(0).toUpperCase() + desc.slice(1);

    const response = await fetch(`/maquina/${window.maquinaAtivaId}/adicionar_tarefa/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ descricao: desc })
    });
    if (response.ok) location.reload();
}

async function toggleTarefa(tarefaId) {
    const response = await fetch(`/tarefa/${tarefaId}/alternar/`, { method: 'POST' });
    if (response.ok) location.reload();
}

async function deletarTarefa(tarefaId) {
    if (!confirm("Excluir esta observação?")) return;
    const response = await fetch(`/tarefa/${tarefaId}/deletar/`, { method: 'POST' });
    if (response.ok) location.reload();
}

// Inicialização instantânea
function inicializar() {
    const ultimaId = localStorage.getItem('ultimaMaquinaSelecionada');
    let alvo = ultimaId ? document.getElementById('maquina-item-' + ultimaId) : document.querySelector('.machine-item');
    if (alvo) alvo.click();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializar);
} else {
    inicializar();
}