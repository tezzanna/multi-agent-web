const _k = atob("MTBmY2U3ZTUwNmFjNGQ1NmYzMjdiOGU0ZGRmYjVmMzU=");

function get_api_key() {
    return _k;
}

async function fetchWeatherData() {
    const city = 'Moscow';
    const apiKey = get_api_key();
    const url = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric&lang=ru`;

    const tempElement = document.getElementById('current-temp');
    const descElement = document.getElementById('weather-desc');
    const forecastElement = document.getElementById('forecast-list');

    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Ошибка API: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();

        // Обновление текущей температуры
        if (tempElement) {
            tempElement.textContent = `${Math.round(data.main.temp)}°C`;
        }

        // Обновление описания погоды
        if (descElement) {
            descElement.textContent = data.weather[0].description;
        }

        // Обновление списка прогноза (в данном примере используем данные о текущей погоде для демонстрации, 
        // так как запрос сделан к endpoint 'weather', а не 'forecast'. 
        // Для полноценного прогноза нужно использовать endpoint /forecast)
        if (forecastElement) {
            forecastElement.innerHTML = '';
            const listItems = [
                { title: 'Ветер', value: `${data.wind.speed} м/с` },
                { title: 'Влажность', value: `${data.main.humidity}%` },
                { title: 'Давление', value: `${data.main.pressure} гПа` },
                { title: 'Ощущается как', value: `${Math.round(data.main.feels_like)}°C` }
            ];

            listItems.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.title}: ${item.value}`;
                forecastElement.appendChild(li);
            });
        }

    } catch (error) {
        console.error(error);
        if (tempElement) tempElement.textContent = 'Ошибка';
        if (descElement) descElement.textContent = 'Не удалось загрузить данные';
        if (forecastElement) forecastElement.textContent = 'Ошибка соединения с API';
    }
}

// Запуск функции при загрузке страницы
document.addEventListener('DOMContentLoaded', fetchWeatherData);