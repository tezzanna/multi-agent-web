const _k = atob("MTBmY2U3ZTUwNmFjNGQ1NmYzMjdiOGU0ZGRmYjVmMzU=");

function get_api_key() {
    return _k;
}

async function fetchWeather() {
    const lat = 55.75; // Москва
    const lon = 37.61;
    const apiKey = get_api_key();
    
    const currentWeatherEl = document.getElementById('current-weather');
    const forecastListEl = document.getElementById('forecast-list');

    try {
        // Запрос текущей погоды
        const currentResponse = await fetch(
            `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric&lang=ru`
        );
        
        if (!currentResponse.ok) throw new Error('Ошибка получения данных о текущей погоде');
        const currentData = await currentResponse.json();

        // Рендеринг текущей погоды
        currentWeatherEl.innerHTML = `
            <h2>${currentData.name}</h2>
            <div class="temp">${Math.round(currentData.main.temp)}°C</div>
            <div class="description">${currentData.weather[0].description}</div>
            <img src="https://openweathermap.org/img/wn/${currentData.weather[0].icon}@2x.png" alt="icon" class="icon">
        `;

        // Запрос прогноза (5-day/3-hour forecast)
        const forecastResponse = await fetch(
            `https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric&lang=ru`
        );

        if (!forecastResponse.ok) throw new Error('Ошибка получения прогноза');
        const forecastData = await forecastResponse.json();

        // Группировка прогноза по дням (берем данные на 3 дня)
        // В API forecast данные идут каждые 3 часа. Возьмем среднее за день или конкретные точки.
        // Для упрощения возьмем данные на 12:00 каждого из следующих 3 дней.
        
        const daysData = [];
        const now = new Date();
        const datesSeen = new Set();

        forecastData.list.forEach(item => {
            const date = new Date(item.dt * 1000);
            const dateStr = date.toDateString(); // Уникальный ключ для дня

            if (!datesSeen.has(dateStr)) {
                datesSeen.add(dateStr);
                daysData.push({
                    date: date,
                    temp: item.main.temp,
                    description: item.weather[0].description,
                    icon: item.weather[0].icon
                });
            }
            
            if (datesSeen.size >= 3) return; // Берем только 3 дня
        });

        // Рендеринг прогноза
        forecastListEl.innerHTML = '';
        daysData.forEach(dayItem => {
            const dayName = dayItem.date.toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' });
            
            const li = document.createElement('li');
            li.className = 'forecast-item';
            li.innerHTML = `
                <div>
                    <span class="day">${dayName}</span>
                    <img src="https://openweathermap.org/img/wn/${dayItem.icon}@2x.png" alt="icon" class="icon">
                </div>
                <div class="temp-range">
                    ${Math.round(dayItem.temp)}°C
                </div>
            `;
            forecastListEl.appendChild(li);
        });

    } catch (error) {
        currentWeatherEl.innerHTML = `<p class="error">Ошибка: ${error.message}</p>`;
        forecastListEl.innerHTML = '';
        console.error(error);
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', fetchWeather);