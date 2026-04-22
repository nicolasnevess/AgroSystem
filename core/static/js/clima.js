async function buscarClima() {
    const key = '804d7b40'; // <--- Coloque sua Key aqui
    const cidadeBusca = 'Piracicaba,SP';
    const url = `https://api.hgbrasil.com/weather?format=json-cors&key=${key}&city_name=${cidadeBusca}`;

    try {
        const response = await fetch(url);
        const data = await response.json();
        const clima = data.results;

        // 1. Atualiza a Temperatura
        const tempElem = document.querySelector('.temp');
        if (tempElem) tempElem.innerHTML = `${clima.temp}°C`;

        // 2. Atualiza a Descrição (Céu Limpo, etc)
        const descElem = document.querySelector('.desc');
        if (descElem) descElem.innerHTML = clima.description;
        
        // 3. Atualiza o Nome da Cidade (A nova linha que adicionamos)
        const cityElem = document.querySelector('.city-name');
        if (cityElem) cityElem.innerHTML = clima.city;

        console.log("Sucesso: Dados de " + clima.city + " injetados no HTML.");
    } catch (error) {
        console.error("Erro na integração:", error);
    }
}

// Roda a função
buscarClima();