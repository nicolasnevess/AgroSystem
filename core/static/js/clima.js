async function buscarClima() {
    const key = '804d7b40';
    const wrapper = document.getElementById('clima-wrapper');
    
    // Pega os dados da 'fazenda_ativa' enviados pela sua view
    const cidadeBanco = wrapper.getAttribute('data-cidade');
    const ufBanco = wrapper.getAttribute('data-uf');

    // Se não houver fazenda (usuário novo), ele não tenta buscar ou usa um padrão
    if (!cidadeBanco || !ufBanco) {
        console.log("Nenhuma fazenda ativa para buscar clima.");
        return;
    }

    const localBusca = `${cidadeBanco},${ufBanco}`;
    const url = `https://api.hgbrasil.com/weather?format=json-cors&key=${key}&city_name=${localBusca}`;

    try {
        const response = await fetch(url);
        const data = await response.json();
        const clima = data.results;

        // Atualiza os elementos na tela
        const tempElem = document.querySelector('.temp');
        const descElem = document.querySelector('.desc');
        const cityElem = document.querySelector('.city-name');

        if (tempElem) tempElem.innerHTML = `${clima.temp}°C`;
        if (descElem) descElem.innerHTML = clima.description;
        if (cityElem) cityElem.innerHTML = clima.city;

        console.log("Clima dinâmico carregado: " + localBusca);
    } catch (error) {
        console.error("Erro na API HG Brasil:", error);
    }
}

buscarClima();