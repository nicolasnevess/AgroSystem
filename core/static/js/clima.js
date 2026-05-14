async function buscarClima() {
    // 1. PRIMEIRO: Definimos o wrapper
    const wrapper = document.getElementById('clima-wrapper');
    
    // Se o wrapper não existir na página, paramos aqui para não dar erro
    if (!wrapper) return;

    // 2. DEPOIS: Pegamos os atributos dele
    const key = wrapper.getAttribute('data-key');
    const cidadeBanco = wrapper.getAttribute('data-cidade');
    const ufBanco = wrapper.getAttribute('data-uf');

    // Verificação
    if (!cidadeBanco || !ufBanco || !key) {
        console.log("Faltam dados (Cidade, UF ou Key) para buscar o clima.");
        return;
    }

    const localBusca = `${cidadeBanco},${ufBanco}`;
    const url = `https://api.hgbrasil.com/weather?format=json-cors&key=${key}&city_name=${localBusca}`;

    try {
        const response = await fetch(url);
        const data = await response.json();
        const clima = data.results;

        // Elementos na tela
        const tempElem = document.querySelector('.temp');
        const descElem = document.querySelector('.desc');
        const cityElem = document.querySelector('.city-name');
        const iconElem = document.getElementById('weather-icon');

        if (tempElem) tempElem.innerHTML = `${clima.temp}°C`;
        if (descElem) descElem.innerHTML = clima.description;
        if (cityElem) cityElem.innerHTML = clima.city;

        // --- LÓGICA DE TROCA DE ÍCONE ---
        if (iconElem) {
            const slug = clima.condition_slug;
            
            // Reseta as classes, mantendo apenas a base do FontAwesome
            iconElem.className = 'fas'; 

            // Mapeamento corrigido
            if (slug.includes('storm')) {
                iconElem.classList.add('fa-bolt');
            } else if (slug.includes('rain')) {
                iconElem.classList.add('fa-cloud-showers-heavy');
            } else if (slug.includes('cloudly_day')) {
                iconElem.classList.add('fa-cloud-sun');
            } else if (slug.includes('cloudly_night')) {
                iconElem.classList.add('fa-cloud-moon');
            } else if (slug.includes('cloud')) {
                iconElem.classList.add('fa-cloud');
            } else if (slug.includes('clear_day')) {
                iconElem.classList.add('fa-sun');
            } else if (slug.includes('clear_night')) {
                iconElem.classList.add('fa-moon');
            } else if (slug.includes('hail')) {
                iconElem.classList.add('fa-icicles');
            } else if (slug.includes('fog')) {
                iconElem.classList.add('fa-smog');
            } else {
                iconElem.classList.add('fa-cloud-sun'); 
            }
        }

        console.log("Clima carregado com sucesso!");
    } catch (error) {
        console.error("Erro na API HG Brasil:", error);
    }
}

// Chama a função
buscarClima();