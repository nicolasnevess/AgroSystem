// Navegação entre fazendas
function navegarFazenda(valor) {
    if (valor === "NOVA") window.location.href = "/configurar-propriedade/";
    else if (valor) window.location.href = "?fazenda_id=" + valor;
}

// Preview da foto no cadastro (Topo da página)
function previewImageEdit(input) {
    const preview = document.getElementById('edit_foto_preview');
    const vazia = document.getElementById('edit_foto_vazia');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
            vazia.style.display = 'none';
        }
        reader.readAsDataURL(input.files[0]);
    }
}

// FUNÇÕES DO MODAL (TELINHA)
function abrirModalEdicao(id, ident, nome, peso, especie, raca, sexo, status, fotoUrl) {
    const modal = document.getElementById('modalEditarAnimal');
    const form = document.getElementById('formEditarAnimal');
    const imgPreview = document.getElementById('edit_foto_preview');
    const imgVazia = document.getElementById('edit_foto_vazia');
    
    // 1. Preenche os campos do formulário
    document.getElementById('edit_identificacao').value = ident;
    document.getElementById('edit_nome').value = nome;
    document.getElementById('edit_peso').value = peso.replace(',', '.');
    document.getElementById('edit_especie').value = especie;
    document.getElementById('edit_raca').value = raca;
    document.getElementById('edit_sexo').value = sexo;
    document.getElementById('edit_status').value = status;
    
    // 2. Define a rota de destino da edição ANTES de abrir
    form.action = "/animais/editar/" + id + "/";
    
    // 3. Lógica da Foto: Esconde um e mostra o outro (Evita sobreposição)
    if (fotoUrl && fotoUrl !== "" && fotoUrl !== "None" && fotoUrl !== "undefined" && fotoUrl !== "null") {
        imgPreview.src = fotoUrl;
        imgPreview.style.display = "block"; // Mostra a imagem
        imgVazia.style.display = "none";    // Esconde o ícone de vez
    } else {
        imgPreview.src = "";
        imgPreview.style.display = "none";  // Esconde a imagem
        imgVazia.style.display = "flex";    // Mostra o ícone centralizado
    }
    
    // 4. ABRE O MODAL (Usando FLEX para garantir a centralização do CSS)
    modal.style.display = "flex";
    
    // 5. TRAVA o scroll da página de baixo
    document.body.style.overflow = "hidden";
}

function fecharModal() {
    const modal = document.getElementById('modalEditarAnimal');
    modal.style.display = "none";
    
    // Libera o scroll da página de baixo
    document.body.style.overflow = "auto";
}

// Fecha o modal se o usuário clicar na área escura (fora da caixa branca)
window.onclick = function(event) {
    const modal = document.getElementById('modalEditarAnimal');
    if (event.target == modal) {
        fecharModal();
    }
}