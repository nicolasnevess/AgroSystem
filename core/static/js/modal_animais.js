// static/js/modal_animais.js
function abrirModalEdicao(id, iden, nome, peso, status, especie, raca, sexo, sanitario, fotoUrl) {
    const modal = document.getElementById('modalEdicao');
    const form = document.getElementById('formEditar');

    form.action = `/animais/editar/${id}/`;

    document.getElementById('edit-iden').value = iden;
    document.getElementById('edit-nome').value = nome;
    document.getElementById('edit-peso').value = peso.replace(',', '.');
    document.getElementById('edit-status').value = status;
    document.getElementById('edit-especie').value = especie;
    document.getElementById('edit-raca').value = raca;
    document.getElementById('edit-sexo').value = sexo;
    document.getElementById('edit-sanitario').value = sanitario;

    const preview = document.getElementById('edit-preview');
    // Verifica se a URL da foto existe e não é "None"
    if (fotoUrl && fotoUrl !== "" && fotoUrl !== "None") {
        preview.src = fotoUrl;
        preview.style.display = 'block';
    } else {
        preview.style.display = 'none';
    }

    modal.style.display = 'flex';
}

function fecharModal() {
    document.getElementById('modalEdicao').style.display = 'none';
}