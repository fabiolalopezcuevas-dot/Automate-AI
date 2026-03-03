from flask import Flask, request, jsonify
import os
import json
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

PROMPT_TEMPLATE = """
Eres un asistente de auditoría interna experto en ciberseguridad.
Recibirás:
- Control: {control}
- Objetivo: {objetivo}
- Alcance: {alcance}

Genera TODO el contenido en una sola respuesta JSON.

Redacción de hallazgo:
- Usa: "No se está asegurando que [qué falla] debido a que [causa raíz], lo que pudiera derivar en [riesgo]"

Anexo completo:
- Qué se hace correctamente
- Qué falta o falla
- Riesgo
- Vectores MITRE ATT&CK
- Recomendaciones (inicia con "Derivado de lo anteriormente mencionado, el equipo de AI recomienda:")
- Referencias (al final en bullets)
- Plan de remediación (enumerado con verbos y evidencia)

Salida JSON:
{
  "redaccion_hallazgo": "...",
  "anexo": "..."
}
"""

@app.route("/generar", methods=["POST"])
def generar():
    data = request.json
    control = data.get("control", "")
    objetivo = data.get("objetivo", "")
    alcance = data.get("alcance", "")

    prompt = PROMPT_TEMPLATE.format(control=control, objetivo=objetivo, alcance=alcance)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un asistente de auditoría interna experto."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    raw = response.choices[0].message["content"]

    try:
        result = json.loads(raw)
        redaccion = result.get("redaccion_hallazgo", "")
        anexo = result.get("anexo", "")
    except:
        redaccion = ""
        anexo = raw

    return jsonify({
        "redaccion_hallazgo": redaccion,
        "anexo": anexo
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
  @app.route("/", methods=["GET"])
def home():
    return "API de auditoría AI funcionando. Usa el endpoint /generar para POST."
