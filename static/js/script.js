console.log("Hello from Flask!");
function fetchWeather() {
    fetch('/get_weather', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            // Display the response in a preformatted text area
            document.getElementById('weatherOutput').textContent = JSON.stringify(data, null, 2);
        })
        .catch(error => console.error('Error:', error));
}
