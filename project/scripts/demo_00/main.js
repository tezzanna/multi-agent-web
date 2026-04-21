document.addEventListener('DOMContentLoaded', () => {
  const _k = atob("MTBmY2U3ZTUwNmFjNGQ1NmYzMjdiOGU0ZGRmYjVmMzU=");
  
  const API_KEY = _k;
  const LAT = 55.7558; // Москва широта
  const LON = 37.6173; // Москва долгота
  const UNITS = 'metric';
  const LANG = 'ru';

  const currentWeatherEl = document.getElementById('current-weather');
  const forecastListEl = document.getElementById('forecast-list');

  async function get_api_key() {
    return API_KEY;
  }

  function renderWeather() {
    currentWeatherEl.innerHTML = '<p>Загрузка данных...</p>';
    forecastListEl.innerHTML = '<p>Загрузка прогноза...</p>';
  }

  function showError(message) {
    currentWeatherEl.innerHTML = `<p class="error">Ошибка: ${message}</p>`;
    forecastListEl.innerHTML = '';
  }

  async function fetchWeatherData() {
    try {
      const key = await get_api_key();
      
      // Запрос к One Call 3.0 (или Forecast 2.5, здесь используется One Call для надежности)
      // Используем текущее время и прогноз на 3 дня (72 часа)
      const url = `https://api.openweathermap.org/data/3.0/onecall?lat=${LAT}&lon=${LON}&exclude=minutely,alerts&units=${UNITS}&lang=${LANG}&appid=${key}`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        if (response.status === 401) throw new Error("Неверный API ключ или лимит превышен");
        if (response.status === 404) throw new Error("Координаты не найдены");
        throw new Error(`Ошибка сети: ${response.status}`);
      }

      const data = await response.json();
      renderResponse(data);

    } catch (error) {
      console.error(error);
      showError(error.message);
    }
  }

  function renderResponse(data) {
    // Рендеринг текущей погоды
    const current = data.current;
    const weatherDesc = current.weather[0].description;
    const temp = Math.round(current.temp);
    const feelsLike = Math.round(current.feels_like);
    const humidity = current.humidity;
    const windSpeed = current.wind_speed;
    const iconCode = current.weather[0].icon;
    const iconUrl = `https://openweathermap.org/img/wn/${iconCode}@2x.png`;

    const currentHtml = `
      <div class="weather-card">
        <img src="${iconUrl}" alt="${weatherDesc}" class="weather-icon">
        <h2>${temp}°C</h2>
        <p class="description">${weatherDesc}</p>
        <div class="details">
          <span>Ощущается как: ${feelsLike}°C</span>
          <span>Влажность: ${humidity}%</span>
          <span>Ветер: ${windSpeed} м/с</span>
        </div>
      </div>
    `;
    currentWeatherEl.innerHTML = currentHtml;

    // Рендеринг прогноза (берем первые 24 часа, раз в 1 час или фильтруем по дням)
    // Для простоты списка возьмем ближайшие 12 часов из hourly массива
    const forecastHtml = data.hourly.slice(0, 12).map(hour => {
      const time = new Date(hour.dt * 1000);
      const timeString = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const hourTemp = Math.round(hour.temp);
      const hourIconCode = hour.weather[0].icon;
      const hourIconUrl = `https://openweathermap.org/img/wn/${hourIconCode}.png`;
      
      return `
        <div class="forecast-item">
          <span class="time">${timeString}</span>
          <img src="${hourIconUrl}" alt="icon" class="forecast-icon">
          <span class="temp">${hourTemp}°C</span>
        </div>
      `;
    }).join('');

    forecastListEl.innerHTML = forecastHtml;
  }

  // Инициализация
  renderWeather();
  fetchWeatherData();
});