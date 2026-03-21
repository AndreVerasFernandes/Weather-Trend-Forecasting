<script setup>
import { computed, ref } from 'vue'

const searchText = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const placeLabel = ref('')
const lastUpdated = ref('')
const current = ref(null)
const daily = ref([])

const weatherCodeMap = {
  0: { text: 'Clear sky', icon: '☀️' },
  1: { text: 'Mainly clear', icon: '🌤️' },
  2: { text: 'Partly cloudy', icon: '⛅' },
  3: { text: 'Overcast', icon: '☁️' },
  45: { text: 'Fog', icon: '🌫️' },
  48: { text: 'Depositing rime fog', icon: '🌫️' },
  51: { text: 'Light drizzle', icon: '🌦️' },
  53: { text: 'Moderate drizzle', icon: '🌦️' },
  55: { text: 'Dense drizzle', icon: '🌧️' },
  56: { text: 'Light freezing drizzle', icon: '🌧️' },
  57: { text: 'Dense freezing drizzle', icon: '🌧️' },
  61: { text: 'Slight rain', icon: '🌧️' },
  63: { text: 'Moderate rain', icon: '🌧️' },
  65: { text: 'Heavy rain', icon: '🌧️' },
  66: { text: 'Light freezing rain', icon: '🌧️' },
  67: { text: 'Heavy freezing rain', icon: '🌧️' },
  71: { text: 'Slight snow fall', icon: '🌨️' },
  73: { text: 'Moderate snow fall', icon: '🌨️' },
  75: { text: 'Heavy snow fall', icon: '❄️' },
  77: { text: 'Snow grains', icon: '❄️' },
  80: { text: 'Slight rain showers', icon: '🌦️' },
  81: { text: 'Moderate rain showers', icon: '🌧️' },
  82: { text: 'Violent rain showers', icon: '⛈️' },
  85: { text: 'Slight snow showers', icon: '🌨️' },
  86: { text: 'Heavy snow showers', icon: '❄️' },
  95: { text: 'Thunderstorm', icon: '⛈️' },
  96: { text: 'Thunderstorm with slight hail', icon: '⛈️' },
  99: { text: 'Thunderstorm with heavy hail', icon: '⛈️' }
}

const hasWeather = computed(() => Boolean(current.value && daily.value.length))

const currentWeatherText = computed(() => {
  if (!current.value) return ''
  return weatherCodeMap[current.value.weather_code]?.text || 'Undefined condition'
})

const currentWeatherIcon = computed(() => {
  if (!current.value) return '🌍'
  return weatherCodeMap[current.value.weather_code]?.icon || '🌍'
})

const smartTips = computed(() => {
  if (!hasWeather.value) return []

  const tips = []
  const today = daily.value[0]

  if (today?.uvIndex >= 8) {
    tips.push('High UV index: sunscreen and sunglasses are recommended.')
  }

  if (today?.rainChance >= 60) {
    tips.push('High chance of rain today: take an umbrella and plan extra travel time.')
  }

  if (Number(current.value?.wind_speed_10m) >= 35) {
    tips.push('Strong winds: avoid unprotected outdoor activities.')
  }

  if (Number(current.value?.apparent_temperature) >= 33) {
    tips.push('High apparent temperature: stay hydrated and prefer shade during peak hours.')
  }

  if (!tips.length) {
    tips.push('Conditions are generally stable. Good time for outdoor activities.')
  }

  return tips
})

function formatDate(inputDate) {
  return new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    day: '2-digit',
    month: '2-digit'
  }).format(new Date(inputDate + 'T00:00:00'))
}

function formatTime(isoString) {
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(isoString))
}

async function geocodePlace(query) {
  const response = await fetch(
    `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(query)}&count=1&language=en&format=json`
  )

  if (!response.ok) {
    throw new Error('Failed to query the geolocation service.')
  }

  const data = await response.json()
  if (!data.results?.length) {
    throw new Error('Location not found. Try a city, postal code, or a more specific landmark.')
  }

  const first = data.results[0]
  const labelParts = [first.name, first.admin1, first.country].filter(Boolean)

  return {
    latitude: first.latitude,
    longitude: first.longitude,
    label: labelParts.join(', ')
  }
}

async function reverseGeocode(latitude, longitude) {
  const response = await fetch(
    `https://geocoding-api.open-meteo.com/v1/reverse?latitude=${latitude}&longitude=${longitude}&language=en&format=json`
  )

  if (!response.ok) {
    return `${latitude.toFixed(2)}, ${longitude.toFixed(2)}`
  }

  const data = await response.json()
  if (!data.results?.length) {
    return `${latitude.toFixed(2)}, ${longitude.toFixed(2)}`
  }

  const first = data.results[0]
  return [first.name, first.admin1, first.country].filter(Boolean).join(', ')
}

async function fetchWeather(latitude, longitude, label) {
  const response = await fetch(
    `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,wind_speed_10m,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,uv_index_max,sunrise,sunset&forecast_days=5&timezone=auto`
  )

  if (!response.ok) {
    throw new Error('Unable to fetch weather data right now. Please try again in a moment.')
  }

  const data = await response.json()
  const dailyPayload = data.daily

  current.value = data.current
  placeLabel.value = label
  lastUpdated.value = new Date().toLocaleString('en-US')

  daily.value = (dailyPayload.time || []).map((day, index) => {
    const code = dailyPayload.weather_code[index]
    return {
      date: day,
      icon: weatherCodeMap[code]?.icon || '🌍',
      weatherText: weatherCodeMap[code]?.text || 'Undefined condition',
      minTemp: dailyPayload.temperature_2m_min[index],
      maxTemp: dailyPayload.temperature_2m_max[index],
      rainChance: dailyPayload.precipitation_probability_max[index],
      uvIndex: dailyPayload.uv_index_max[index],
      sunrise: dailyPayload.sunrise[index],
      sunset: dailyPayload.sunset[index]
    }
  })
}

function resetError() {
  errorMessage.value = ''
}

async function searchByText() {
  if (!searchText.value.trim()) {
    errorMessage.value = 'Please enter a location to fetch the weather.'
    return
  }

  isLoading.value = true
  resetError()

  try {
    const place = await geocodePlace(searchText.value.trim())
    await fetchWeather(place.latitude, place.longitude, place.label)
  } catch (error) {
    errorMessage.value = error.message || 'Unexpected error while fetching weather data.'
  } finally {
    isLoading.value = false
  }
}

async function searchByCurrentLocation() {
  if (!navigator.geolocation) {
    errorMessage.value = 'Your browser does not support geolocation.'
    return
  }

  isLoading.value = true
  resetError()

  try {
    const position = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 30000
      })
    })

    const latitude = position.coords.latitude
    const longitude = position.coords.longitude
    const label = await reverseGeocode(latitude, longitude)

    await fetchWeather(latitude, longitude, `${label} (your location)`)
  } catch {
    errorMessage.value = 'Could not retrieve your location. Please check browser permissions.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="panel">
      <header class="hero">
        <h1>Weather App in Vue</h1>
        <p>
          Search by city, postal code, landmark, or use your current location to get real-time weather.
        </p>
      </header>

      <form class="search-form" @submit.prevent="searchByText">
        <label for="location">Location</label>
        <div class="search-row">
          <input
            id="location"
            v-model="searchText"
            type="text"
            placeholder="Ex: New York, 10001, Times Square"
            :disabled="isLoading"
          />
          <button type="submit" :disabled="isLoading">Search weather</button>
          <button type="button" class="ghost" :disabled="isLoading" @click="searchByCurrentLocation">
            Use my location
          </button>
        </div>
      </form>

      <p v-if="isLoading" class="status">Loading weather data...</p>
      <p v-if="errorMessage" class="status error">{{ errorMessage }}</p>

      <section v-if="hasWeather" class="results" aria-live="polite">
        <article class="current-card">
          <div>
            <p class="place">{{ placeLabel }}</p>
            <p class="updated">Updated at {{ lastUpdated }}</p>
          </div>
          <div class="now">
            <span class="icon">{{ currentWeatherIcon }}</span>
            <div>
              <p class="temp">{{ current.temperature_2m }}°C</p>
              <p>{{ currentWeatherText }}</p>
            </div>
          </div>
          <div class="metrics">
            <p>Feels like: {{ current.apparent_temperature }}°C</p>
            <p>Humidity: {{ current.relative_humidity_2m }}%</p>
            <p>Precipitation: {{ current.precipitation }} mm</p>
            <p>Wind: {{ current.wind_speed_10m }} km/h</p>
          </div>
        </article>

        <section class="tips-card">
          <h2>What to consider beyond temperature</h2>
          <ul>
            <li v-for="tip in smartTips" :key="tip">{{ tip }}</li>
          </ul>
        </section>

        <section class="forecast">
          <h2>5-day forecast</h2>
          <div class="forecast-grid">
            <article v-for="day in daily" :key="day.date" class="day-card">
              <p class="date">{{ formatDate(day.date) }}</p>
              <p class="day-icon">{{ day.icon }}</p>
              <p class="desc">{{ day.weatherText }}</p>
              <p>Max: {{ day.maxTemp }}°C</p>
              <p>Min: {{ day.minTemp }}°C</p>
              <p>Rain: {{ day.rainChance }}%</p>
              <p>UV: {{ day.uvIndex }}</p>
              <p>Sunrise: {{ formatTime(day.sunrise) }}</p>
              <p>Sunset: {{ formatTime(day.sunset) }}</p>
            </article>
          </div>
        </section>
      </section>
    </section>
  </main>
</template>
