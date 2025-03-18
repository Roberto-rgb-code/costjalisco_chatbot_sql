from flask import Flask, request, jsonify
from flask_cors import CORS
from decouple import config
import mysql.connector
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# Cargar credenciales desde .env
XAI_API_KEY = config('XAI_API_KEY')
DB_CONFIG = {
    "host": config("DB_HOST"),
    "user": config("DB_USER"),
    "password": config("DB_PASSWORD"),
    "database": config("DB_NAME")
}

# Conectar con OpenAI para xAI API
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

# Contexto de CoST Jalisco
cost_description = """
La iniciativa de Transparencia en Infraestructura [Construction Sector Transparency Initiative] o "CoST" por sus siglas en inglés, es la encargada de promover la transparencia y la rendición de cuentas dentro de las diferentes etapas de los proyectos de infraestructura y obra pública.

Actualmente, tiene presencia en 19 países distribuidos en cuatro continentes, donde trabaja directamente con el Gobierno, la sociedad civil y la industria del ramo de la construcción para promover la divulgación, validación e interpretación de datos de proyectos de infraestructura y obra pública.


"""

# Conectar a la base de datos MySQL
def conectar_bd():
    return mysql.connector.connect(**DB_CONFIG)

# 🔹 NUEVO: Función para obtener información de proyectos y estadísticas
def obtener_datos(user_message):
    user_message = user_message.lower()

    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    # 🔍 Query COMPLETA para obtener información de proyectos
    if "proyectos" in user_message or "infraestructura" in user_message:
        query = """
        SELECT p.id, p.title, p.description, ps.titulo as estado, 
            sect.titulo as sector, pt.titulo as tipo, 
            pc.montocontrato as presupuesto_monto, pc.fechapublicacion as fecha_aprobacion,
            pf.fechafinalizacion as fecha_fin, pf.costofinalizacion as valor_final,
            l.lat, l.lng, l.description as location_name,
            o.id as id_organization, o.name as organization_name
        FROM project p
        LEFT JOIN projectstatus ps ON p.status = ps.id
        LEFT JOIN projectsector sect ON p.sector = sect.id
        LEFT JOIN projecttype pt ON p.type = pt.id
        LEFT JOIN proyecto_contratacion pc ON p.id = pc.id_project
        LEFT JOIN proyecto_finalizacion pf ON p.id = pf.id_project
        LEFT JOIN project_locations pl ON p.id = pl.id_project
        LEFT JOIN locations l ON pl.id_location = l.id
        LEFT JOIN project_organizations po ON p.id = po.id_project
        LEFT JOIN organization o ON po.id_organization = o.id
        WHERE pc.montocontrato IS NOT NULL
        ORDER BY p.id
        LIMIT 5
        """
        cursor.execute(query)
        proyectos = cursor.fetchall()
        conn.close()
        respuesta = "\n".join([
            f"📌 {p['title']} ({p['estado']}) - {p['description']}\n"
            f"📍 Ubicación: {p['location_name']} (Lat: {p['lat']}, Lng: {p['lng']})\n"
            f"💰 Presupuesto: ${p['presupuesto_monto']:,.2f} MXN\n"
            f"🏗️ Sector: {p['sector']} | Tipo: {p['tipo']}\n"
            f"🏛️ Organización: {p['organization_name']}\n"
            f"📅 Fecha de Aprobación: {p['fecha_aprobacion']} | Fecha de Finalización: {p['fecha_fin']}\n"
            for p in proyectos
        ])
        return respuesta if respuesta else "No hay proyectos registrados en la base de datos."

    # 📊 ESTADÍSTICAS GENERALES
    elif "presupuesto total" in user_message or "dinero invertido" in user_message:
        query = "SELECT SUM(pc.montocontrato) as total_presupuesto FROM proyecto_contratacion pc"
        cursor.execute(query)
        resultado = cursor.fetchone()
        presupuesto = resultado["total_presupuesto"] if resultado["total_presupuesto"] else 0
        conn.close()
        return f"💰 El presupuesto total de los proyectos en CoST Jalisco es de **${presupuesto:,.2f} MXN**."

    elif "cantidad de proyectos" in user_message or "cuántos proyectos" in user_message:
        query = "SELECT COUNT(*) as total_proyectos FROM project"
        cursor.execute(query)
        resultado = cursor.fetchone()
        total_proyectos = resultado["total_proyectos"]
        conn.close()
        return f"📊 Actualmente, hay **{total_proyectos} proyectos** en CoST Jalisco."

    elif "sectores más activos" in user_message or "infraestructura más desarrollada" in user_message:
        query = """
        SELECT sect.titulo as sector, COUNT(p.id) as total_proyectos
        FROM project p
        LEFT JOIN projectsector sect ON p.sector = sect.id
        GROUP BY sect.titulo
        ORDER BY total_proyectos DESC
        LIMIT 3
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        conn.close()
        sectores = "\n".join([f"🔹 {s['sector']}: {s['total_proyectos']} proyectos" for s in resultados])
        return f"🏗️ Los sectores más activos en CoST Jalisco son:\n{sectores}"

    elif "impacto" in user_message or "beneficiarios" in user_message:
        query = "SELECT SUM(p.beneficiarios) as total_beneficiarios FROM project p"
        cursor.execute(query)
        resultado = cursor.fetchone()
        beneficiarios = resultado["total_beneficiarios"] if resultado["total_beneficiarios"] else 0
        conn.close()
        return f"👥 Más de **{beneficiarios:,} personas** han sido beneficiadas por los proyectos en CoST Jalisco."

    conn.close()
    return None  # Si la pregunta no es sobre estadísticas ni proyectos, sigue con el chatbot normal.

# Ruta del chatbot
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').lower()
    model = data.get('model', 'grok-2-latest')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # 📌 Si la pregunta es sobre estadísticas o proyectos, responde con datos de MySQL
    respuesta_bd = obtener_datos(user_message)
    if respuesta_bd:
        return jsonify({'response': respuesta_bd})

    # 📌 Si la pregunta no es sobre estadísticas ni proyectos, usa xAI
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"Eres Grok, asistente de CoST Jalisco. {cost_description}"},
                {"role": "user", "content": user_message},
            ],
        )
        bot_response = completion.choices[0].message.content
        return jsonify({'response': bot_response})
    except Exception as e:
        return jsonify({'response': f"Error en la API: {e}"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
