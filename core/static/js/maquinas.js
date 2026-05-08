// core/static/js/maquinas.js

window.maquinaAtivaId = null;

/**
 * Atualiza o painel de detalhes lateral ao clicar em uma máquina da lista
 */
function atualizarDetalhes(elemento, nome, modelo, horimetro, fazenda, identificacao, pk_banco) {
    window.maquinaAtivaId = pk_banco;
    
    // Salva no navegador qual máquina está aberta para persistência
    localStorage.setItem('ultimaMaquinaSelecionada', pk_banco);

    // Gerencia o destaque visual (seleção) na lista da esquerda
    document.querySelectorAll('.machine-item').forEach(item => {
        item.classList.remove('active');
    });
    elemento.classList.add('active');

    // Preenche os dados textuais no painel da direita
    document.getElementById('view-titulo').innerText = nome + " " + modelo;
    document.getElementById('view-horimetro').innerText = horimetro;
    document.getElementById('view-fazenda').innerText = fazenda;
    document.getElementById('view-id').innerText = identificacao;

    // Atualiza as URLs dos botões de ação (Editar/Excluir máquina)
    atualizarLinksAcao(pk_banco);

    // Renderiza as observações específicas desta máquina
    renderizarTarefasVisuais(pk_banco);
}

/**
 * Redireciona para a troca de fazenda ou cadastro de nova
 */
function navegarFazenda(valor) {
    if (valor === "NOVA") {
        window.location.href = "/propriedade/configurar/"; 
    } else if (valor) {
        localStorage.removeItem('ultimaMaquinaSelecionada');
        window.location.href = "?fazenda_id=" + valor;
    }
}

/**
 * Atualiza os links dos botões de Editar e Deletar máquina
 */
function atualizarLinksAcao(id) {
    const linkEditar = document.getElementById('link-editar-maquina');
    const linkDeletar = document.getElementById('link-deletar-maquina');
    
    if (id && linkEditar && linkDeletar) {
        linkEditar.href = `/maquinas/editar/${id}/`;
        linkDeletar.href = `/maquinas/deletar/${id}/`;
        linkEditar.style.display = 'flex';
        linkDeletar.style.display = 'flex';
    }
}

/**
 * Lê os dados ocultos do HTML e monta a lista de observações no painel lateral
 */
function renderizarTarefasVisuais(maquinaId) {
    const container = document.getElementById('container-tarefas');
    const dadosOcultos = document.getElementById('tarefas-data-' + maquinaId);
    
    if (!container) return;
    container.innerHTML = ''; 

    if (dadosOcultos && dadosOcultos.children.length > 0) {
        Array.from(dadosOcultos.children).forEach(span => {
            const idTarefa = span.getAttribute('data-id');
            const concluida = span.getAttribute('data-concluida') === 'true';
            const dataCriacao = span.getAttribute('data-data');
            const texto = span.innerText;

            container.innerHTML += `
                <div class="task-item" id="tarefa-item-${idTarefa}" style="display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 10px; background: #f9f9f9; padding: 10px; border-radius: 8px; border-left: 4px solid ${concluida ? '#888' : '#4b6630'};">
                    <div style="display: flex; align-items: center; gap: 10px; flex: 1;">
                        <input type="checkbox" ${concluida ? 'checked' : ''} onchange="toggleTarefa(${idTarefa})" style="cursor: pointer; transform: scale(1.2);">
                        <span id="texto-tarefa-${idTarefa}" style="${concluida ? 'text-decoration: line-through; color: #888;' : 'color: #333; font-weight: 500;'}">
                            ${texto}
                        </span>
                    </div>
                    
                    <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 2px;">
                        <small style="color: #999; font-size: 0.7rem;">
                            <i class="fas fa-calendar-alt"></i> ${dataCriacao || ''}
                        </small>
                        <button onclick="deletarTarefa(${idTarefa})" style="background: none; border: none; color: #e74c3c; cursor: pointer; padding: 5px;">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>`;
        });
    } else {
        container.innerHTML = '<p style="color: #999; font-size: 0.85rem; text-align: center; padding: 20px;">Nenhuma observação registrada.</p>';
    }
}

/**
 * Adiciona uma nova observação sem recarregar a página
 */
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

    if (response.ok) {
        const data = await response.json(); 
        const container = document.getElementById('container-tarefas');
        
        // Atualiza o painel visual (o que você está vendo agora)
        if (container.querySelector('p')) container.innerHTML = '';

        const novaTarefaHtml = `
            <div class="task-item" id="tarefa-item-${data.id}" style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee; background: #f9f9f9; border-left: 4px solid #4b6630; margin-bottom: 10px; border-radius: 8px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <input type="checkbox" onchange="toggleTarefa(${data.id})">
                    <span id="texto-tarefa-${data.id}">${data.descricao}</span>
                </div>
                <div style="text-align: right;">
                    <small style="display: block; color: #888; font-size: 0.7rem;">
                        <i class="fas fa-calendar-alt"></i> ${data.data_criacao}
                    </small>
                    <button onclick="deletarTarefa(${data.id})" style="color: #ff4d4f; border: none; background: none; cursor: pointer;">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('afterbegin', novaTarefaHtml);

        // Salva na "biblioteca escondida" para persistir ao trocar de máquina
        const bibliotecaOculta = document.getElementById('tarefas-data-' + window.maquinaAtivaId);
        if (bibliotecaOculta) {
            const novoSpanOculto = `
                <span data-id="${data.id}" 
                      data-concluida="false" 
                      data-data="${data.data_criacao}">
                    ${data.descricao}
                </span>`;
            bibliotecaOculta.insertAdjacentHTML('afterbegin', novoSpanOculto);
        }

        input.value = ''; 
    }
}

/**
 * Alterna o status de concluído (Riscado) na hora, sem recarregar
 */
async function toggleTarefa(tarefaId) {
    const response = await fetch(`/tarefa/${tarefaId}/alternar/`, { method: 'POST' });
    if (response.ok) {
        const span = document.getElementById(`texto-tarefa-${tarefaId}`);
        const item = document.getElementById(`tarefa-item-${tarefaId}`);
        
        if (span.style.textDecoration === 'line-through') {
            span.style.textDecoration = 'none';
            span.style.color = '#333';
            item.style.borderLeftColor = '#4b6630';
        } else {
            span.style.textDecoration = 'line-through';
            span.style.color = '#888';
            item.style.borderLeftColor = '#888';
        }
    }
}

/**
 * Deleta a tarefa e remove o elemento da tela na hora
 */
async function deletarTarefa(tarefaId) {
    if (!confirm("Excluir esta observação?")) return;
    
    const response = await fetch(`/tarefa/${tarefaId}/deletar/`, { method: 'POST' });
    
    if (response.ok) {
        // Remove do painel de visualização (o que você está vendo agora)
        const elementoVisual = document.getElementById(`tarefa-item-${tarefaId}`);
        if (elementoVisual) {
            elementoVisual.style.opacity = '0';
            setTimeout(() => elementoVisual.remove(), 300);
        }

        // Remove da div escondida (para não voltar ao trocar de máquina)
        // Procuramos o span dentro de qualquer div de tarefas que tenha o data-id correto
        const spanOculto = document.querySelector(`span[data-id="${tarefaId}"]`);
        if (spanOculto) {
            spanOculto.remove();
        }
    } else {
        alert("Erro ao excluir a tarefa no servidor.");
    }
}

/**
 * Inicialização: abre a última máquina selecionada ou a primeira da lista
 */
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

