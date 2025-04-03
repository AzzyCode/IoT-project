let sensorChart_temp_humidity;
let sensorChart_pressure;

async function fetchSensorData() {
  try {
    const response = await fetch('/sensor-data');
    const data = await response.json();

    if (data.length === 0) {
      return;
    }

    // Reverse data to show oldest first
    data.reverse();

    const timestamps = data.map(d => d.datetime);
    const temperatures = data.map(d => parseFloat(d.temperature));
    const humidities = data.map(d => parseFloat(d.humidity));
    const pressures = data.map(d => parseFloat(d.pressure)); // ✅ Extract pressure data

    // Update the sensor values displayed
    document.getElementById('temperature').textContent = temperatures[temperatures.length - 1];
    document.getElementById('humidity').textContent = humidities[humidities.length - 1];
    document.getElementById('pressure').textContent = pressures[pressures.length - 1]; // ✅ Corrected variable & spelling

    // Update charts
    updateChart(timestamps, temperatures, humidities, pressures);
  } catch (error) {
    console.error('Error fetching sensor data:', error);
  }
}

function createChart() {
  const ctx1 = document.getElementById('sensorChart_temp_humidity').getContext('2d');
  const ctx2 = document.getElementById('sensorChart_pressure').getContext('2d');

  sensorChart_temp_humidity = new Chart(ctx1, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Temperature (°C)',
          data: [],
          borderColor: 'red',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderWidth: 2,
          fill: true
        },
        {
          label: 'Humidity (%)',
          data: [],
          borderColor: 'blue',
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderWidth: 2,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          ticks: { autoSkip: true, maxTicksLimit: 10 },
          title: { display: true, text: 'Time' }
        },
        y: {
          beginAtZero: false,
          title: { display: true, text: 'Value' }
        }
      }
    }
  });

  sensorChart_pressure = new Chart(ctx2, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Pressure (hPa)',
          data: [],
          borderColor: 'green',
          backgroundColor: 'rgba(41, 195, 108, 0.2)',
          borderWidth: 2,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          ticks: { autoSkip: true, maxTicksLimit: 10 },
          title: { display: true, text: 'Time' }
        },
        y: {
          beginAtZero: false,
          title: { display: true, text: 'Value' }
        }
      }
    }
  });
}

function updateChart(labels, tempData, humData, pressureData) { // ✅ Added pressureData parameter
  // Update Temperature & Humidity chart
  sensorChart_temp_humidity.data.labels = labels;
  sensorChart_temp_humidity.data.datasets[0].data = tempData;
  sensorChart_temp_humidity.data.datasets[1].data = humData;
  sensorChart_temp_humidity.update();

  // Update Pressure chart
  sensorChart_pressure.data.labels = labels;
  sensorChart_pressure.data.datasets[0].data = pressureData;
  sensorChart_pressure.update();
}

// Launch the graph and update every 2s
document.addEventListener('DOMContentLoaded', () => {
  createChart();
  fetchSensorData();
  setInterval(fetchSensorData, 2000);
});
