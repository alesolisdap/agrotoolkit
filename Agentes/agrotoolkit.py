import os
from flask import Flask, request, jsonify, render_template_string
import openai
import requests
from datetime import datetime, timedelta, time

app = Flask(__name__)

# Load OpenAI API key from environment variable for safety
openai.api_key = ""

FRONTEND_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
<title>🌾 Agrotoolkit AI</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: 'Montserrat', sans-serif;
    background: linear-gradient(135deg, #266b38, #498565);
    color: #000000;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    padding: 1rem;
  }
  header {
    text-align: center;
    margin-bottom: 1rem;
  }
  header h1 {
    font-weight: 700;
    font-size: 1.8rem;
    margin-bottom: 0.3rem;
  }
  header p {
    font-weight: 400;
    font-size: 1rem;
    opacity: 0.8;
  }
  main {
    background: #f0fff2dd;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    flex-grow: 1;
    max-width: 800px;
    width:800px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
  }
  label {
    font-weight: 600;
    margin: 0.5rem 0 0.2rem 0;
  }
  select{
    padding: 0.6rem;
    border-radius: 8px;
    border: 2px solid #266b38;
    font-size: 1rem;
    width: 100%;
    transition: border-color 0.3s ease;
  }
  select:focus {
    outline: none;
    border-color: #4A2511;
    background-color: #fff9f2;
  }
  input[type="number"] {
    padding: 0.6rem;
    border-radius: 8px;
    border: 2px solid #266b38;
    font-size: 1rem;
    width: 100%;
    transition: border-color 0.3s ease;
  }
  input[type="number"]:focus {
    outline: none;
    border-color: #4A2511;
    background-color: #fff9f2;
  }
  button {
    background-color: #266b38;
    color: #f4ecd8;
    padding: 0.8rem;
    margin-top: 1rem;
    font-weight: 700;
    font-size: 1.1rem;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    box-shadow: 0 5px 10px #4a2511cc;
    transition: background-color 0.3s ease;
  }
  button:hover {
    background-color: #15430d;
  }
  #response {
    margin-top: 1.2rem;
    white-space: pre-wrap;
    background: #edffe6;
    padding: 0.8rem;
    border-radius: 10px;
    min-height: 120px;
    box-shadow: inset 0 0 5px rgba(107,66,38,0.3);
    overflow-y: auto;
  }
  footer {
    margin-top: 1rem;
    font-size: 0.8rem;
    text-align: center;
    color: #000000;
  }
  @media (max-width: 400px) {
    main {
      max-width: 100%;
      padding: 0.8rem;
    }
    button {
      font-size: 1rem;
      padding: 0.7rem;
    }
  }
</style>
</head>
<body>
<header>
  <h1>🌾 Agrotoolkit AI</h1>
  <p>Ingresa coordenadas para recibir indicaciones fenológicas.</p>
  
</header>
<main>
  <label for="latitude">Latitud</label>
  <input type="number" id="latitude" step="0.000001" min="-90" max="90" placeholder="Ejemplo: -3.745" />
  <label for="longitude">Longitud</label>
  <input type="number" id="longitude" step="0.000001" min="-180" max="180" placeholder="Ejemplo: -73.253" />
  <label for="activity">Actividad de la finca</label>
  <select id="activity">
    <option value="cafe">Café</option>
    <option value="platano">Plátano</option>
    <option value="maiz">Maíz</option>
    <option value="frijol">Frijol</option>
    <option value="ganado bovino engorde">Ganado Bovino (Engorde)</option>
    <option value="ganado bovino (producción de leche)">Ganado Bovino (Producción de leche)</option>
    <option value="ganado porcino ">Ganado Porcino</option>
    <option value="avicola ">Aves</option>
    <option value="apicultura">Apicultura</option>

    <option value="otros">Otros</option>
  </select>
  <button id="btnSubmit">Obtener indicaciones fenológicas</button>
  <textarea id="response" readonly="readonly" rows="8"></textarea>
</main>
<footer>
  © 2025 - 🌾 Agrotoolkit AI.
</footer>

<script>
  const btn = document.getElementById('btnSubmit');
  const responseEl = document.getElementById('response');

  btn.addEventListener('click', async () => {
    responseEl.textContent = '';
    const lat = parseFloat(document.getElementById('latitude').value);
    const lon = parseFloat(document.getElementById('longitude').value);
    const activity = document.getElementById('activity').value;
    if (isNaN(lat) || lat < -90 || lat > 90) {
      alert('Por favor, ingresa una latitud válida entre -90 y 90.');
      return;
    }
    if (isNaN(lon) || lon < -180 || lon > 180) {
      alert('Por favor, ingresa una longitud válida entre -180 y 180.');
      return;
    }

    btn.disabled = true;
    btn.textContent = 'Consultando...';

    try {
      const response = await fetch('/api/phenology', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ latitude: lat, longitude: lon , activity: activity}),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Error en la respuesta del servidor.');
      }
      const data = await response.json();
      responseEl.textContent = data.result;
    } catch (error) {
      responseEl.textContent = 'Error: ' + error.message;
    } finally {
      btn.disabled = false;
      btn.textContent = 'Obtener indicaciones fenológicas';
    }
  });
</script>
</body>
</html>
"""
import requests
from datetime import datetime, timedelta, time
from collections import defaultdict

def fetch_meteorological_history():
    station_id = "234423908"
    today = datetime.utcnow()
    f2_datetime = datetime.combine(today.date(), time.min)
    f1_datetime = f2_datetime - timedelta(days=30)

    f1 = f1_datetime.strftime("%Y-%m-%d %H:%M:%S")
    f2 = f2_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    url = (
        f"https://gc.meteo.tech/_api.php?op=history&station_id={station_id}&variable_id=0"
        f"&f1={f1}&f2={f2}"
    )

    # Define variables a procesar y sus reglas
    variables = {
        "TMP": {"name": "Temperatura (°C)", "unit": "°C", "min": 0, "max": 40, "type": "mean"},
        "HRP": {"name": "Humedad relativa (%)", "unit": "%", "min": 0, "max": 100, "type": "mean"},
        "PP":  {"name": "Precipitación (mm)", "unit": "mm", "min": 0, "max": 200, "type": "sum"},
        "PCA": {"name": "Precipitación acumulada (mm)", "unit": "mm", "min": 0, "max": 1000, "type": "sum"},
        "RSOL": {"name": "Radiación solar (W/m²)", "unit": "W/m²", "min": 0, "max": 1500, "type": "mean"},
        "UV": {"name": "Índice UV", "unit": "", "min": 0, "max": 15, "type": "mean"},
        "WNS": {"name": "Velocidad del viento (km/h)", "unit": "km/h", "min": 0, "max": 150, "type": "mean"},
    }

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f"Error al obtener datos meteorológicos: status {response.status_code}"
        
        data = response.json()
        if not isinstance(data, list) or not data:
            return "No se encontraron datos meteorológicos en el periodo solicitado."

        # Agrupar valores por variable
        grouped = defaultdict(list)
        for rec in data:
            var = rec.get("variable_name")
            val = rec.get("num_value")
            if var in variables and isinstance(val, (int, float)):
                vmeta = variables[var]
                if vmeta["min"] <= val <= vmeta["max"]:
                    grouped[var].append(val)

        if not grouped:
            return "No se encontraron registros válidos dentro de los rangos definidos."

        # Construir resumen
        resumen = "Resumen de datos meteorológicos del último mes:"
        for var, vals in grouped.items():
            meta = variables[var]
            if not vals:
                continue
            if meta["type"] == "mean":
                avg = sum(vals) / len(vals)
                resumen += f"\n- {meta['name']}: media {avg:.1f}{meta['unit']}, máx {max(vals):.1f}, mín {min(vals):.1f}"
            elif meta["type"] == "sum":
                total = sum(vals)
                resumen += f"\n- {meta['name']}: total {total:.1f}{meta['unit']}"

        resumen += f"\n- Registros procesados: {len(data)} (filtrados por variable y rango)"
        return resumen

    except Exception as e:
        return f"Excepción al obtener datos meteorológicos: {str(e)}"



@app.route('/')
def index():
    return render_template_string(FRONTEND_HTML)

@app.route('/api/phenology', methods=['POST'])
def phenology():
    #if not OPENAI_API_KEY:
    #    return jsonify({"error": "La clave API de OpenAI no está configurada en el servidor."}), 500
    data = request.get_json()
    lat = data.get("latitude")
    lon = data.get("longitude")
    activity = data.get("activity")

    meteo_summary = fetch_meteorological_history()
    if lat is None or lon is None:
        return jsonify({"error": "Se requieren latitud y longitud."}), 400
    try:
        lat = float(lat)
        lon = float(lon)
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return jsonify({"error": "Coordenadas fuera de rango."}), 400
    except ValueError:
        return jsonify({"error": "Latitud o longitud no válidas."}), 400

    app.logger.info('Actividad: %s',activity)
    app.logger.info('Meteo: %s',meteo_summary)
    prompt = (
        f"Eres un experto en fenología y estás asesorando a un agricultor sobre {activity}.\n"
        f"Debes generar recomendaciones fenológicas personalizadas para la actividad {activity} en las coordenadas: latitud {lat}, longitud {lon}.\n"
        f"Inicia tu respuesta con un resumen claro y conciso de la información meteorológica histórica, especialmente los datos de temperatura, que se encuentra en esta variable:\n{meteo_summary}\n"
        "Utiliza estos datos climáticos para contextualizar las fases fenológicas de la actividad seleccionada en esa región.\n"
        "Incluye recomendaciones agrícolas específicas para cada fase, considerando prácticas adecuadas según el clima típico y los cuidados necesarios del cultivo.\n"
        "Además, considera los siguientes casos de uso y plantillas:\n"
        "- Predicción de enfermedades\n"
        "- Optimización de riego\n"
        "- Monitoreo de cultivos\n"
        "- Trazabilidad de productos agrícolas\n"
        "Incorpora palabras clave estratégicas como Agricultura de Precisión, Computer Vision, Análisis Predictivo, Blockchain Agrícola, y más, para enriquecer la respuesta.\n"
        "La respuesta debe ser útil para la toma de decisiones prácticas en campo. Evita formatos de texto como negritas, pero asegúrate de que sea clara y estructurada."
    )


    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            store=True,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        answer = completion.choices[0].message.content.strip()
        return jsonify({"result": answer})
    except Exception  as e:
        return jsonify({"error": f"Error en API OpenAI: {str(e)}"}), 500

if __name__ == '__main__':
    # Run app on localhost with debug off for production use disable debug
    app.run(host='0.0.0.0', port=5000, debug=True)