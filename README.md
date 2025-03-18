📌 README.md - Chatbot CoST Jalisco
markdown
Copiar
Editar
# 🏗️ Chatbot CoST Jalisco - Transparencia en Infraestructura

Este proyecto es un **chatbot inteligente** desarrollado en **Flask**, que permite a los usuarios consultar información en tiempo real sobre los proyectos de infraestructura en **CoST Jalisco**. Los datos provienen de una **base de datos MySQL**, garantizando información actualizada sobre presupuesto, sectores activos, número de beneficiarios y más.

---

## 📌 **Características del Proyecto**
✅ **Consulta en tiempo real** de información sobre proyectos de infraestructura.  
✅ **Extracción de estadísticas** como presupuesto total, número de proyectos y sectores más activos.  
✅ **Respuestas dinámicas** utilizando la API de **xAI** cuando no hay coincidencias en la base de datos.  
✅ **Interfaz con Power BI**, permitiendo visualizar los datos en un dashboard interactivo.  
✅ **Widget de chatbot con imagen personalizada** para facilitar la interacción.

---

## 📌 **Tecnologías Utilizadas**
🔹 **Backend:** Flask, Flask-CORS, MySQL Connector, OpenAI API  
🔹 **Base de Datos:** MySQL  
🔹 **Frontend:** HTML, CSS, JavaScript  
🔹 **Visualización de Datos:** Power BI  

---

## 🚀 **1. Instalación y Configuración**
### 📌 **Requisitos Previos**
Antes de comenzar, asegúrate de tener instalado:
- **Python 3.8+**
- **MySQL**
- **Un entorno virtual (opcional, pero recomendado)**

### 📌 **1.1 Clonar el Repositorio**
```bash
git clone https://github.com/tu-usuario/chatbot-cost-jalisco.git
cd chatbot-cost-jalisco
📌 1.2 Crear un Entorno Virtual (Opcional)
bash
Copiar
Editar
# En Linux / Mac
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
venv\Scripts\activate
📌 1.3 Instalar Dependencias
bash
Copiar
Editar
pip install -r requirements.txt
📌 1.4 Configurar Variables de Entorno
Crea un archivo .env en la raíz del proyecto y agrega tus credenciales:

ini
Copiar
Editar
XAI_API_KEY=tu_api_key_xai
DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=tu_basededatos
🛠️ 2. Configuración de la Base de Datos
Ejecuta la siguiente query en MySQL para asegurarte de que los datos están estructurados correctamente:

sql
Copiar
Editar
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
ORDER BY p.id;
🚀 3. Ejecución del Proyecto
📌 3.1 Levantar el Servidor Flask
Para iniciar el backend, ejecuta:

bash
Copiar
Editar
python app.py
El servidor correrá en http://localhost:5000.

🌐 4. Uso del Chatbot
📌 Interfaz con Power BI
Para visualizar los proyectos en un dashboard interactivo, abre el archivo index.html en tu navegador.

📌 Widget del Chatbot
Para activar el chatbot, haz clic en el botón flotante.
Puedes hacer preguntas como:
pgsql
Copiar
Editar
1️⃣ ¿Cuáles son los proyectos en CoST Jalisco?
2️⃣ ¿Cuál es el presupuesto total de CoST Jalisco?
3️⃣ ¿Cuántos proyectos hay en CoST Jalisco?
4️⃣ ¿Cuáles son los sectores con más infraestructura?
5️⃣ ¿Cuántas personas han sido beneficiadas por estos proyectos?
📌 Ejemplo de Respuesta del Chatbot
markdown
Copiar
Editar
📊 Actualmente, hay **154 proyectos** en CoST Jalisco.
