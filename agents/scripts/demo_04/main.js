const API_KEY = 'YOUR_API_KEY';
const LAT = 55.7558;
const LON = 37.6173;
const DAYS_TO_FETCH = 3;

function init() {
    const url = `https://api.openweathermap.org/data/2.5/onecall?lat=${LAT}&lon=${LON}&appid=${API_KEY}&units=metric&exclude=current,minutely,alerts`;
    
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const filteredDays = getWeatherForNextDays(data.daily, DAYS_TO_FETCH);
            renderWeatherCards(filteredDays);
        })
        .catch(error => {
            const errorElement = document.getElementById('error-message');
            if (errorElement) {
                errorElement.textContent = `Ошибка загрузки данных: ${error.message}`;
            } else {
                console.error('Ошибка инициализации:', error);
            }
        });
}

function getWeatherForNextDays(dailyData, count) {
    const today = new Date();
    const result = [];
    
    for (let i = 0; i < count; i++) {
        const dayData = dailyData[i];
        if (!dayData) break;

        const dateObj = new Date(dayData.dt * 1000);
        const dayOfWeek = dateObj.toLocaleDateString('ru-RU', { weekday: 'long' });
        const dayDate = dateObj.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
        const temp = Math.round(dayData.temp.day);
        const condition = dayData.weather[0].description;
        const iconCode = dayData.weather[0].icon;
        const iconUrl = `https://openweathermap.org/img/wn/${iconCode}@2x.png`;

        result.push({
            date: `${dayOfWeek}, ${dayDate}`,
            temp: temp,
            condition: condition,
            icon: iconUrl
        });
    }
    return result;
}

function renderWeatherCards(daysData) {
    const container = document.getElementById('weather-container');
    if (!container) return;

    container.innerHTML = '';

    daysData.forEach(day => {
        const card = document.createElement('div');
        card.className = 'weather-card';

        const dateDisplay = document.createElement('div');
        dateDisplay.id = 'date-display';
        dateDisplay.textContent = day.date;

        const tempDisplay = document.createElement('div');
        tempDisplay.id = 'temp-display';
        tempDisplay.textContent = `${day.temp}°C`;

        const conditionDisplay = document.createElement('div');
        conditionDisplay.id = 'condition-display';
        conditionDisplay.textContent = day.condition;

        const iconDisplay = document.createElement('img');
        iconDisplay.id = 'icon-display';
        iconDisplay.src = day.icon;
        iconDisplay.alt = day.condition;
        iconDisplay.style.width = '64px';
        iconDisplay.style.height = '64px';

        card.appendChild(dateDisplay);
        card.appendChild(iconDisplay);
        card.appendChild(tempDisplay);
        card.appendChild(conditionDisplay);

        container.appendChild(card);
    });
}

document.addEventListener('DOMContentLoaded', init);