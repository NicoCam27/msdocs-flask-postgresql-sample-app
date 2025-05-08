import os
from zoneinfo import ZoneInfo
import ntplib
from datetime import datetime, timezone
from zoneinfo import ZoneInfo  # Use 'pytz' if Python < 3.9

from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask import request, jsonify
from sqlalchemy import desc

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)


# The import must be done after db initialization due to circular import issue
from models import  Imagen


@app.route('/', methods=['GET'])
def index():
    print('Request for index page received')
    imagenes = Imagen.query.order_by(desc(Imagen.fecha)).all()
    return render_template('index.html', imagenes=imagenes)

@app.route('/crear_imagen_manualmente', methods=['GET'])
def crear_imagen_manualmente():
    print('Peticion para acceder a la prueba de pagina principal')
    return render_template('crear_imagen_manualmente.html')

@app.route('/add', methods=['POST'])
@csrf.exempt
def add_imagen():
    try:
        username = request.values.get('username') #username
        nombre_archivo = request.values.get('nombre_archivo') #nombre_archivo
        n_pixeles_total = request.values.get('n_pixeles_total') #n_pixeles_total
        tipo_transformacion = request.values.get('tipo_transformacion') #tipo_transformacion
        n_pixeles_azules = request.values.get('n_pixeles_azules') #n_pixeles_azules
        n_pixeles_verdes = request.values.get('n_pixeles_verdes') #n_pixeles_verdes
        n_pixeles_rojos = request.values.get('n_pixeles_rojos') #n_pixeles_rojos
    except (KeyError):
        # Redisplay the question voting form.
        return render_template('add_imagen.html', {
            'error_message': "You must include a username, filename, number of pixeles, transformation types and number of blue, green and red and the date at least*",
        })
    else:

        imagen = Imagen()
        imagen.user_name = username
        imagen.nombre_archivo = nombre_archivo
        imagen.n_pixeles_total = n_pixeles_total
        imagen.tipo_transformacion = tipo_transformacion
        imagen.n_pixeles_azules = n_pixeles_azules
        imagen.n_pixeles_verdes = n_pixeles_verdes
        imagen.n_pixeles_rojos = n_pixeles_rojos

        client = ntplib.NTPClient()
        response = client.request('ntp.roa.es')
        utc_dt = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
        madrid_dt = utc_dt.astimezone(ZoneInfo("Europe/Madrid"))
        formatted = madrid_dt.strftime("%Y-%m-%d %H:%M:%S")
        imagen.fecha = formatted
        
        db.session.add(imagen)
        db.session.commit()

        return redirect(url_for('index'))
    

@app.route('/api/imagenes', methods=['POST'])
@csrf.exempt  # Only for testing or trusted clients. Don't use in production without auth.
def api_add_imagen():
    data = request.get_json()

    client = ntplib.NTPClient()
    response = client.request('ntp.roa.es')
    utc_dt = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
    madrid_dt = utc_dt.astimezone(ZoneInfo("Europe/Madrid"))
    formatted = madrid_dt.strftime("%Y-%m-%d %H:%M:%S")

    imagen = Imagen(
        user_name=data.get('user_name'),
        nombre_archivo=data.get('nombre_archivo'),
        n_pixeles_total=data.get('n_pixeles_total'),
        tipo_transformacion=data.get('tipo_transformacion'),
        n_pixeles_azules=data.get('n_pixeles_azules'),
        n_pixeles_verdes=data.get('n_pixeles_verdes'),
        n_pixeles_rojos=data.get('n_pixeles_rojos'),
        fecha = formatted
    )
    db.session.add(imagen)
    db.session.commit()
    return jsonify({"status": "success", "id": imagen.id}), 201


@app.route('/<int:id>', methods=['POST'])
@csrf.exempt
def borrar(id):
    imagen = Imagen.query.get(id)
    if imagen:
        # Also delete related reviews or images if needed (cascade manually if not using ON DELETE CASCADE in DB)
        db.session.delete(imagen)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return f"No se encontró ningún restaurante con id {id}", 404
    

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
