document.addEventListener('DOMContentLoaded', () => {
    const _k = atob("MTBmY2U3ZTUwNmFjNGQ1NmYzMjdiOGU0ZGRmYjVmMzU=");
    const LAT = 55.7558;
    const LON = 37.6173;
    const CONTAINER_ID = 'weather-container';
    const DAYS_TO_SHOW = 3;

    const container = document.getElementById(CONTAINER_ID);

    if (!container) {
        console.error(`Container with ID "${CONTAINER_ID}" not found.`);
        return;
    }

    async function fetchWeatherData() {
        const url = `https://api.openweathermap.org/data/2.5/forecast?lat=${LAT}&lon=${LON}&appid=${_k}&units=metric`;

        try {
            const response = await fetch(url);
            
            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('Ошибка доступа: Неверный API ключ');
                } else if (response.status === 404) {
                    throw new Error('Ошибка: Координаты не найдены');
                } else {
                    throw new Error(`Ошибка сервера: ${response.status}`);
                }
            }

            const data = await response.json();
            
            if (!data.list) {
                throw new Error('Некорректный формат ответа от API');
            }

            processData(data.list);

        } catch (error) {
            console.error('Ошибка при получении данных:', error);
            container.innerHTML = `<div class="error-message">Ошибка: ${error.message}</div>`;
        }
    }

    function processData(list) {
        // Фильтрация: берем первый список прогноза на каждый из 3 дней
        // API возвращает данные каждые 3 часа. Нам нужно найти уникальные даты.
        const uniqueDates = new Set();
        const filteredData = [];

        for (const item of list) {
            const date = new Date(item.dt * 1000);
            const dateKey = date.toLocaleDateString(); // Используем локализованную строку даты для группировки

            if (!uniqueDates.has(dateKey)) {
                uniqueDates.add(dateKey);
                filteredData.push({
                    ...item,
                    dateKey: dateKey,
                    dateObj: date
                });
            }

            if (uniqueDates.size >= DAYS_TO_SHOW) {
                break;
            }
        }

        renderCards(filteredData);
    }

    function renderCards(data) {
        container.innerHTML = '';

        data.forEach(item => {
            const card = document.createElement('div');
            card.className = 'weather-card';

            const dateStr = item.dateObj.toLocaleDateString('ru-RU', {
                weekday: 'long',
                day: 'numeric',
                month: 'long'
            });

            const temp = Math.round(item.main.temp);
            const description = item.weather[0].description;
            const iconUrl = `https://openweathermap.org/img/wn/${item.weather[0].icon}@2x.png`;

            card.innerHTML = `
                <div class="card-date">${dateStr}</div>
                <div class="card-icon">
                    <img src="${iconUrl}" alt="${description}">
                </div>
                <div class="card-temp">${temp}°C</div>
                <div class="card-desc">${description}</div>
            `;

            container.appendChild(card);
        });
    }

    fetchWeatherData();
});