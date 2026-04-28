async function buscarClima() {
    const key = '804d7b40';
    const wrapper = document.getElementById('clima-wrapper');
    
    const cidadeBanco = wrapper.getAttribute('data-cidade');
    const ufBanco = wrapper.getAttribute('data-uf');

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

        // Elementos na tela
        const tempElem = document.querySelector('.temp');
        const descElem = document.querySelector('.desc');
        const cityElem = document.querySelector('.city-name');
        const iconElem = document.getElementById('weather-icon'); // Seleciona o ícone

        if (tempElem) tempElem.innerHTML = `${clima.temp}°C`;
        if (descElem) descElem.innerHTML = clima.description;
        if (cityElem) cityElem.innerHTML = clima.city;

        // --- LÓGICA DE TROCA DE ÍCONE ---
        if (iconElem) {
            const slug = clima.condition_slug;
            
            // Resetamos as classes do FontAwesome para garantir que não fiquem ícones duplicados
            iconElem.className = 'fas'; 

            // Mapeamento de Slugs da HG Brasil para ícones do FontAwesome
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
                iconElem.classList.add('fa-cloud-sun'); // Ícone padrão caso não encontre
            }
        }

        console.log("Clima dinâmico carregado com ícone: " + clima.condition_slug);
    } catch (error) {
        console.error("Erro na API HG Brasil:", error);
    }
}

buscarClima();