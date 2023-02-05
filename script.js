const loader = document.querySelector('.loader');
const temperature = document.querySelector('#temperature');
const humidity = document.querySelector('#humidity');

async function loaded() {
  loader.classList.add('visible');
  await fetchSensorData();
  loader.classList.remove('visible');

  setInterval(fetchSensorData, 30 * 1000);
}

async function buttonHandle() {
  loader.classList.add('visible');
  await fetchSensorData();
  loader.classList.remove('visible');
}

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchSensorData() {
  try {
    const response = await fetch('/sensor');
    const data = await response.json();

    await sleep(500);

    temperature.innerHTML = `${data.temperature}&#8451;`;
    humidity.innerHTML = `${data.humidity}%`;
  } catch (error) {
    console.error(error);
  }
}

document.addEventListener('DOMContentLoaded', loaded);
document.querySelector('#reloadData').addEventListener('click', buttonHandle);
