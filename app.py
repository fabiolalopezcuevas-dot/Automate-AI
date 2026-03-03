from flask import Flask, request, render_template_string, jsonify
import os
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Página web con formulario
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Auditoría Interna - Ciberseguridad</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
        input, textarea { width: 100%; padding: 10px; margin: 5px 0 20px; }
        button { padding: 10px 20px; font-size: 16px; }
        pre { background: #f4f4f4; padding: 15px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>Generador de Auditoría Interna</h1>
    <form id="auditForm">
        <label>Control:</label>
        <textarea name="control" required></textarea>
        <label>Objetivo:</label>
        <textarea name="objetivo" required></textarea>
        <label>Alcance:</label>
        <textarea name="alcance" required></textarea>
        <button type="submit">Generar</button>
    </form>
    <h2>Resultado:</h2>
    <pre id="resultado"></pre>

    <script>
        const form = document.getElementById("auditForm");
        const resultado = document.getElementById("resultado");

        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            resultado.textContent = "Generando...";
            
            const data = {
                control: form.control.value,
                objetivo: form.objetivo.value,
                alcance: form.alcance.value
            };

            try {
                const response = await fetch("/auditoria", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });

                const resData = await response.json();
                if(resData.resultado) {
                    resultado.textContent = resData.resultado;
                } else {
                    resultado.textContent = "Error: " + resData.error;
                }
            } catch (err) {
                resultado.textContent = "Error: " + err.message;
            }
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/auditoria", methods=["POST"])
def auditoria():
    data = request.json
    control = data.get("control")
    objetivo = data.get("objetivo")
    alcance = data.get("alcance")

    if not control or not objetivo or not alcance:
        return jsonify({"error": "Faltan campos: control, objetivo o alcance"}), 400

    prompt = f"""
Eres un asistente de auditoría interna experto en ciberseguridad.
Recibirás:
- Control: {control}
- Objetivo: {objetivo}
- Alcance: {alcance}

Genera TODO el análisis, hallazgos, anexos y planes de remediación sugeridos.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en auditoría interna de ciberseguridad."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        resultado = response.choices[0].message.content
        return jsonify({"resultado": resultado})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
