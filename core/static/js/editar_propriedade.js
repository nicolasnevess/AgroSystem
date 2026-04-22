document.addEventListener('DOMContentLoaded', function() {
    const selectEstado = document.getElementById('estado');
    const selectCidade = document.getElementById('cidade');

    // Recupera o que está gravado no Django
    const ufSalva = selectEstado.getAttribute('data-uf-salva');
    const cidadeSalva = selectCidade.getAttribute('data-cidade-salva');

    // 1. Carrega os Estados
    fetch('https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome')
        .then(res => res.json())
        .then(estados => {
            estados.forEach(estado => {
                const option = document.createElement('option');
                option.value = estado.sigla;
                option.textContent = estado.nome;
                
                // Se for o estado do banco, deixa selecionado
                if (estado.sigla === ufSalva) {
                    option.selected = true;
                }
                selectEstado.appendChild(option);
            });

            // Se já tinha estado salvo, carrega as cidades dele
            if (ufSalva) {
                carregarCidades(ufSalva, cidadeSalva);
            }
        });

    // 2. Evento ao mudar o estado manualmente
    selectEstado.addEventListener('change', function() {
        carregarCidades(this.value);
    });

    function carregarCidades(uf, cidadeParaSelecionar = null) {
        if (!uf) return;

        selectCidade.disabled = true;
        selectCidade.innerHTML = '<option value="">Carregando cidades...</option>';

        fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${uf}/municipios?orderBy=nome`)
            .then(res => res.json())
            .then(cidades => {
                selectCidade.innerHTML = '<option value="">Selecione a Cidade</option>';
                
                cidades.forEach(cidade => {
                    const option = document.createElement('option');
                    option.value = cidade.nome;
                    option.textContent = cidade.nome;
                    
                    // Se for a cidade do banco, deixa selecionada
                    if (cidadeParaSelecionar && cidade.nome === cidadeParaSelecionar) {
                        option.selected = true;
                    }
                    selectCidade.appendChild(option);
                });
                selectCidade.disabled = false;
            });
    }
});