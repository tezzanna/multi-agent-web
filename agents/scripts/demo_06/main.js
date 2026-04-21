document.addEventListener('DOMContentLoaded', () => {
    // Декодирование ключа
    const _k = atob("MTBmY2U3ZTUwNmFjNGQ1NmYzMjdiOGU0ZGRmYjVmMzU=");

    // Координаты Москвы
    const LAT = 55.7558;
    const LON = 37.6173;

    // URL запроса
    const url = `https://api.openweathermap.org/data/3.0/onecall?lat=${LAT}&lon=${LON}&exclude=minutely,alerts&units=metric&lang=ru&appid=${_k}`;

    // Элементы DOM
    const currentWeatherEl = document.getElementById('current-weather');
    const forecastContainerEl = document.getElementById('forecast-container');

    // Функция форматирования даты
    function formatDate(timestamp) {
        const date = new Date(timestamp * 1000);
        return date.toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' });
    }

    // Функция форматирования времени
    function formatTime(timestamp) {
        const date = new Date(timestamp * 1000);
        return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    }

    // Выполнение запроса
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка сети или неверный API ключ');
            }
            return response.json();
        })
        .then(data => {
            // Обновление текущей погоды
            const current = data.current;
            currentWeatherEl.innerHTML = `
                <div class="temp">${Math.round(current.temp)}°C</div>
                <div class="description">${current.weather[0].description}</div>
            `;

            // Генерация карточек прогноза (36-часовые интервалы)
            // OpenWeatherMap One Call 3.0 возвращает hourly данные
            const hourlyData = data.hourly;
            
            // Нам нужно 3 дня (3 интервала по 36 часов)
            // Индексы: 0 (сейчас), 36 (через 36 часов), 72 (через 72 часов)
            // Если нужно именно "ближайшие 3 дня" в будущем, берем индексы 36, 72, 108
            
            const forecastIndices = [36, 72, 108];

            forecastContainerEl.innerHTML = ''; // Очистка контейнера

            forecastIndices.forEach(index => {
                const forecastItem = hourlyData[index];
                if (!forecastItem) return;

                const card = document.createElement('div');
                card.className = 'forecast-card';
                card.innerHTML = `
                    <div class="date">${formatDate(forecastItem.dt)}</div>
                    <div class="time">${formatTime(forecastItem.dt)}</div>
                    <div class="icon">
                        <img src="https://openweathermap.org/img/wn/${forecastItem.weather[0].icon}@2x.png" alt="${forecastItem.weather[0].description}">
                    </div>
                    <div class="temp">${Math.round(forecastItem.temp)}°C</div>
                    <div class="description">${forecastItem.weather[0].description}</div>
                `;
                forecastContainerEl.appendChild(card);
            });
        })
        .catch(error => {
            console.error('Ошибка получения данных:', error);
            currentWeatherEl.textContent = 'Ошибка загрузки данных';
        });
});