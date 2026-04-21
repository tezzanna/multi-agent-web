const _k = atob("MTBmY2U3ZTUwNmFjNGQ1NmYzMjdiOGU0ZGRmYjVmMzU=");

const API_KEY = _k;
const CITY = "Moscow";
const BASE_URL = "https://api.openweathermap.org/data/2.5/forecast";

function get_api_key() {
    return API_KEY;
}

async function fetchWeatherData() {
    const apiKey = get_api_key();
    const url = `${BASE_URL}?q=${CITY}&appid=${apiKey}&units=metric&lang=ru`;

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Ошибка сети: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        throw error;
    }
}

function filterDataFor3Days(list) {
    const filtered = [];
    const dateMap = new Map();

    list.forEach(item => {
        const date = new Date(item.dt * 1000);
        const dateKey = date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });

        // Фильтруем данные каждые 24 часа (примерно в 12:00)
        if (date.getHours() === 12) {
            // Проверяем, не добавлен ли уже этот день, чтобы избежать дубликатов
            if (!dateMap.has(dateKey)) {
                dateMap.set(dateKey, item);
                filtered.push({
                    ...item,
                    formattedDate: dateKey
                });
            }
        }
    });

    return filtered.slice(0, 3);
}

function renderWeather(data) {
    const container = document.getElementById('weather-container');
    const errorElement = document.getElementById('error-message');

    if (!container || !errorElement) return;

    errorElement.textContent = '';
    container.innerHTML = '';

    data.forEach(day => {
        const temp = Math.round(day.main.temp);
        const description = day.weather[0].description;
        const iconCode = day.weather[0].icon;
        const iconUrl = `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
        const date = day.formattedDate;

        const card = document.createElement('div');
        card.className = 'weather-card';
        card.innerHTML = `
            <h3>${date}</h3>
            <img src="${iconUrl}" alt="${description}">
            <p class="temp">${temp}°C</p>
            <p class="desc">${description}</p>
        `;

        container.appendChild(card);
    });
}

function showError(message) {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.textContent = `Ошибка: ${message}`;
    }
}

async function handleWeatherRequest() {
    const btn = document.getElementById('weather-btn');
    if (btn) btn.disabled = true;

    try {
        const data = await fetchWeatherData();
        const filteredData = filterDataFor3Days(data.list);
        renderWeather(filteredData);
    } catch (error) {
        showError(error.message || 'Не удалось получить данные о погоде');
    } finally {
        if (btn) btn.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('weather-btn');
    if (btn) {
        btn.addEventListener('click', handleWeatherRequest);
    }
});