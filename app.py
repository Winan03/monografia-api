from flask import Flask, request, render_template, redirect, url_for, send_file, flash, session, jsonify
import os
import uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import json
from utils.procesador_pdf import ProcesadorPDF
from generador import GeneradorMonografia
from planes import PlanesManager
import sqlite3


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'clave_de_backup')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['GENERATED_FOLDER'] = 'generated'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Crear directorios necesarios
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)


from flask_cors import CORS

CORS(app, supports_credentials=True)

# Configuración de base de datos SQLite
def init_db():
    conn = sqlite3.connect('monografia_app.db')
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            plan TEXT DEFAULT 'gratis',
            fecha_suscripcion DATETIME,
            fecha_expiracion DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de monografías generadas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monografias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            titulo TEXT NOT NULL,
            tema TEXT NOT NULL,
            archivo_path TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Inicializar base de datos
init_db()

# Instanciar manejadores
planes_manager = PlanesManager()
generador = GeneradorMonografia()
procesador_pdf = ProcesadorPDF()

# Archivos permitidos
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_plan(user_id):
    """Obtiene el plan actual del usuario"""
    conn = sqlite3.connect('monografia_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT plan, fecha_expiracion FROM usuarios WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        plan, fecha_exp = result
        if fecha_exp and datetime.fromisoformat(fecha_exp) < datetime.now():
            # Plan expirado, volver a gratis
            update_user_plan(user_id, 'gratis')
            return 'gratis'
        return plan
    return 'gratis'

def update_user_plan(user_id, plan):
    """Actualiza el plan del usuario"""
    conn = sqlite3.connect('monografia_app.db')
    cursor = conn.cursor()
    
    fecha_exp = None
    if plan != 'gratis':
        fecha_exp = (datetime.now() + timedelta(days=30)).isoformat()
    
    cursor.execute(
        'UPDATE usuarios SET plan = ?, fecha_suscripcion = ?, fecha_expiracion = ? WHERE id = ?',
        (plan, datetime.now().isoformat(), fecha_exp, user_id)
    )
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/planes')
def planes():
    return render_template('planes.html', planes=planes_manager.get_planes())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('monografia_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM usuarios WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['user_email'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas')
    
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    
    conn = sqlite3.connect('monografia_app.db')
    cursor = conn.cursor()
    
    try:
        password_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO usuarios (email, password_hash) VALUES (?, ?)', 
                      (email, password_hash))
        conn.commit()
        flash('Usuario registrado exitosamente')
    except sqlite3.IntegrityError:
        flash('El email ya está registrado')
    finally:
        conn.close()
    
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_plan = get_user_plan(session['user_id'])
    
    # Obtener monografías del usuario
    conn = sqlite3.connect('monografia_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT titulo, tema, created_at FROM monografias WHERE usuario_id = ? ORDER BY created_at DESC', 
                  (session['user_id'],))
    monografias = cursor.fetchall()
    conn.close()
    
    return render_template('dashboard.html', 
                         user_plan=user_plan, 
                         monografias=monografias,
                         funcionalidades=planes_manager.get_funcionalidades_plan(user_plan))

@app.route('/generar', methods=['POST'])
def generar_monografia():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuario no autenticado'}), 401
    
    user_plan = get_user_plan(session['user_id'])
    
    # Datos del formulario
    tema = request.form.get('tema')
    carrera = request.form.get('carrera')
    nivel = request.form.get('nivel')
    extension = request.form.get('extension')
    formato_cita = request.form.get('formato_cita')
    
    # Validar que el usuario tenga permisos
    funcionalidades = planes_manager.get_funcionalidades_plan(user_plan)
    
    if not tema:
        return jsonify({'error': 'El tema es obligatorio'}), 400
    
    try:
        # Procesar archivo PDF si se subió
        contenido_pdf = None
        if 'archivo_pdf' in request.files:
            file = request.files['archivo_pdf']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 
                                      f"{session['user_id']}_{uuid.uuid4()}_{filename}")
                file.save(filepath)
                contenido_pdf = procesador_pdf.extraer_texto(filepath)
        
        # Generar monografía según el plan
        monografia_data = {
            'tema': tema,
            'carrera': carrera,
            'nivel': nivel,
            'extension': int(extension) if extension else 10,
            'formato_cita': formato_cita,
            'contenido_pdf': contenido_pdf,
            'plan': user_plan
        }
        
        resultado = generador.generar_monografia(monografia_data, funcionalidades)
        
        # Guardar en base de datos
        conn = sqlite3.connect('monografia_app.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO monografias (usuario_id, titulo, tema) VALUES (?, ?, ?)',
            (session['user_id'], resultado['titulo'], tema)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'monografia': resultado,
            'plan': user_plan
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/descargar/<tipo>')
def descargar_monografia(tipo):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Aquí implementarías la lógica para generar y descargar el PDF
    # Por ahora retorna un mensaje
    flash(f'Descarga de {tipo} iniciada')
    return redirect(url_for('dashboard'))

@app.route('/actualizar_plan', methods=['POST'])
def actualizar_plan():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuario no autenticado'}), 401
    
    nuevo_plan = request.json.get('plan')
    
    if nuevo_plan not in ['gratis', '5', '10', '20']:
        return jsonify({'error': 'Plan inválido'}), 400
    
    # Aquí implementarías la lógica de pago
    # Por ahora solo actualizamos el plan
    update_user_plan(session['user_id'], nuevo_plan)
    
    return jsonify({'success': True, 'message': f'Plan actualizado a ${nuevo_plan}'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)