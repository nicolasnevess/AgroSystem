document.addEventListener('DOMContentLoaded', function() {
    const selectEstado = document.getElementById('estado');
    const selectCidade = document.getElementById('cidade');

    // Busca os Estados no IBGE e preenche o select
    fetch('https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome')
        .then(response => response.json())
        .then(estados => {
            estados.forEach(estado => {
                const option = document.createElement('option');
                option.value = estado.sigla; // Valor que vai pro banco
                option.textContent = estado.nome; // Texto que o usuário vê
                selectEstado.appendChild(option);
            });
        })
        .catch(error => console.error('Erro ao buscar estados:', error));

    // Quando o usuário escolhe um estado, busca as cidades daquela UF
    selectEstado.addEventListener('change', function() {
        const uf = this.value;
        
        // Reseta o select de cidade
        selectCidade.innerHTML = '<option value="">Selecione a Cidade</option>';
        selectCidade.disabled = true;

        if (uf) {
            fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${uf}/municipios?orderBy=nome`)
                .then(response => response.json())
                .then(cidades => {
                    cidades.forEach(cidade => {
                        const option = document.createElement('option');
                        option.value = cidade.nome;
                        option.textContent = cidade.nome;
                        selectCidade.appendChild(option);
                    });
                    selectCidade.disabled = false; // Libera o campo cidade
                })
                .catch(error => console.error('Erro ao buscar cidades:', error));
        }
    });
});