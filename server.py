from flask import Flask, Response, send_from_directory, render_template_string, jsonify
import threading
import time
import random
import os

app = Flask(__name__)
request_count = 0
lock = threading.Lock()

# HTML con video en streaming basado en peticiones y gráfico en tiempo real
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Servidor en Tiempo Real</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        let requestData = [];
        let requestLabels = [];
        let chart;

        function updateData() {
            fetch('/api/count')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('counter').innerText = data.count;
                    requestData.push(data.count);
                    requestLabels.push(new Date().toLocaleTimeString());

                    if (requestData.length > 20) { 
                        requestData.shift();
                        requestLabels.shift();
                    }

                    chart.data.labels = requestLabels;
                    chart.data.datasets[0].data = requestData;
                    chart.update();
                });
        }

        window.onload = function() {
            let ctx = document.getElementById('trafficChart').getContext('2d');
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Peticiones en Tiempo Real',
                        borderColor: 'red',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        data: []
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: { display: true },
                        y: { beginAtZero: true }
                    }
                }
            });

            setInterval(updateData, 1000);
        };
    </script>
    <style>
        body { text-align: center; font-family: Arial, sans-serif; }
        video { width: 70%; border: 5px solid black; border-radius: 10px; margin-top: 20px; }
        canvas { margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Servidor en Tiempo Real</h1>
    <h2>Peticiones Procesadas: <span id="counter">0</span></h2>
    
    <h3>Gráfico de Peticiones</h3>
    <canvas id="trafficChart" width="600" height="300"></canvas>

    <h3>Reproduciendo Video desde el Servidor</h3>
    <video id="video" controls autoplay>
        Tu navegador no soporta la reproducción de video.
    </video>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <script>
        if (Hls.isSupported()) {
            var video = document.getElementById('video');
            var hls = new Hls();
            hls.loadSource('/video_playlist.m3u8');
            hls.attachMedia(video);
            hls.on(Hls.Events.MANIFEST_PARSED, function () {
                video.play();
            });
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
            video.src = '/video_playlist.m3u8';
            video.addEventListener('canplay', function () {
                video.play();
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/api/data')
def get_data():
    global request_count
    with lock:
        request_count += 1
    time.sleep(random.uniform(0.3, 0.8))  # Simula un tiempo de respuesta variable
    return jsonify({"message": "Datos enviados correctamente", "status": "OK"})

@app.route('/api/count')
def get_count():
    global request_count
    with lock:
        return jsonify({"count": request_count})


# Función para simular un retraso aleatorio
def random_delay():
    delay = random.uniform(0.1, 1.0)  # Retraso aleatorio entre 0.1 y 1 segundo
    time.sleep(delay)

# Servir la lista de reproducción
@app.route('/video_playlist.m3u8')
def video_playlist():
    return send_from_directory(".", "video_playlist.m3u8", mimetype="application/vnd.apple.mpegurl")

# Servir los fragmentos de video con retraso ocasional
@app.route('/<filename>.ts')
def video_segments(filename):
    random_delay()  # Introduce un retraso aleatorio antes de servir el fragmento
    return send_from_directory(".", f"{filename}.ts", mimetype="video/mp2t")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
