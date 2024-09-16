import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
from PySQLiteDBConnection import Connect
from dotenv import load_dotenv, set_key as dset_key
from cryptography.fernet import Fernet
from flask_mail import Mail, Message

app = Flask("Work Solution")

load_dotenv()

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = secrets.token_hex(64)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'uworksolution@gmail.com'
app.config['MAIL_PASSWORD'] = 'onji izse aazu qrkm'
app.config['MAIL_DEFAULT_SENDER'] = ('Work Solution', 'noreply@worksolution.com')

ekey = os.getenv("ENCRYPTION_KEY")

if ekey is None:
    ekey = Fernet.generate_key().decode()
    dotenv_path = ".env"

    dset_key(dotenv_path, "ENCRYPTION_KEY", ekey)

app.config['KEY'] = ekey.encode()


mail = Mail(app)

connection = Connect('data\\database.sqlite3')

EXTENSIONS = {
    'pdf': 'pdf',
    'doc': 'docs',
    'docx': 'docs',
    'jpg': 'image',
    'jpeg': 'image',
    'png': 'image',
    'webp': 'image',
    'pptx': 'powerpoint',
    'txt': 'text',
    'xls': 'calcs',
    'xlsx': 'calcs',
    'zip': 'compress',
    'rar': 'compress',
    'tar': 'compress',
    '7z': 'compress',
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSIONS.keys()


def get_files():
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        files.append({
            'name': filename,
            'type': filename.split('.')[-1],
            'icon': get_file_icon(filename)
        })
    return files


def rename_duplicates(name):
    names = [file["name"] for file in get_files()]
    if name not in names:
        return name
    name_parts = name.rsplit('.', 1)
    name_parts[0] += " (duplicado)"
    new_name = '.'.join(name_parts)
    return rename_duplicates(new_name)


def get_file_icon(filename):
    extension = filename.split('.')[-1]
    return f"{EXTENSIONS.get(extension, 'file.png')}.webp"


def encrypt(key):
    cipher_suite = Fernet(app.config['KEY'])
    return cipher_suite.encrypt(key.encode('utf-8'))


def decrypt(encrypted_key):
    cipher_suite = Fernet(app.config['KEY'])
    return cipher_suite.decrypt(encrypted_key).decode('utf-8')


@app.route('/')
def index():
    user = session.get('email')
    print(f"User: {user}")
    return render_template('index.html', files=get_files(), user=user)


@app.route('/login')
def login():
    if 'email' in session:
        return redirect(url_for('index'))
    else:
        return render_template('login.html')


@app.route('/validate', methods=['POST'])
def validate():
    connection.connect()
    username = request.form['username']
    password = request.form['password']
    data = connection.read_table_with_condition(
        'users', {'email': username}
    )
    connection.close()
    if data and password == decrypt(data[0][3]):
        session['email'] = data[0][2]
        session['id'] = data[0][0]
        session['name'] = data[0][1]
        return redirect(url_for('index'))
    flash('Credencialees inválidas', 'error')
    return redirect(url_for('login'))


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/register', methods=['POST'])
def register():
    connection.connect()
    data = {
        'name': request.form['name'],
        'email': request.form['email'],
        'password': request.form['password'],
    }
    repassword = request.form['repassword']
    if connection.read_table_with_condition('users', {'email': data['email']}):
        flash('Usuario ya existente', 'error')
        connection.close()
        return redirect(url_for('signup'))
    if data['password'] != repassword:
        flash('Las contraseñas no coinciden', 'error')
        connection.close()
        return redirect(url_for('signup'))
    data['password'] = encrypt(repassword)
    connection.insert_into_table('users', data)
    connection.close()
    flash('Registro exitoso', 'success')
    return redirect(url_for('login'))


@app.route('/password')
def password():
    return render_template('password.html')


@app.route("/send-mail", methods=["POST"])
def send_mail():
    connection.connect()
    email = request.form['email']
    data = connection.read_table_with_condition(
        'users', {'email': email}
    )
    if data:
        html_body = f"""
            <html lang="es">
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f9; border-radius: 8px; border: 1px solid #e5e5e5;">
                    <div style="text-align: center;">
                        <!-- Logo de Work Solution -->
                        <img src="https://lh3.googleusercontent.com/fife/ALs6j_F_OsQvW_8CHA3DcZGKgZeZioBYbwnvYWHfdX8wr1W4Mr4hHMYrl0qN0N-OOMki-JMEK3hdLvbqtZVuOOFTZidssVN4WApGHHfEXO255F4ZntWx021FhDq1JE2EGHg2zKwv_a5MALClOkUXxw_g8TYB61UKZoM5ix4O7zzUGvZpXK_jc1lddw-Xw5XbTRD0iSrOdAw44Sh1i0tbRcRNXGgnLt6rMfRqDfUHSFhAEUH6QjKCEFuxsJTSORiBOUHLbVeA9vo-Zvx_kihylhiVpzvJewcBWa8BUBTs7YOIU2jaRMBmgjSEWUl3pj_meVExKVnWZf2ZI5_IoyisHAQPYu1CSQ-x8BVQ_8s74wQhY6WRT_IwfLGHTwbxV-nGtXYUvY0x-mjkk0mxwWb9d9g3mqJc0SwX4Ts_GhsjyaSA774lWgMQ0vxT3hu8XSWdaHiK4K08K4DnuPQrNGk5TMlKwHC2rjFSyaJOWFAAHtS9_fQcECrcjoJmUPyREQCuDP90uNo3rvJ7e3GsIlVaNCAwNc0ZMOsLgSFAeMktV2eXYZlckGmvA7Yx8v3_WoeAo4rdsYtXZxYmwluqdewkMqUva9NlW-Eax_X56ee7DL93LqmtZQWWVp94k-RhsLX4m6O0V6n2UZDNjTE3ehKItU3G8oaYoffGPWHVGrQHH38vt1bATdMdj1aSMqZFiCKxp1vrQju311N1kSduXFNfSGPWa_56u2--4E1ZvMIO32_tqUDSIyKX4gXqvM7DuOBVCKLjW4MbBbFehKFEaB93TohH7feNORmiLBJP-D2NARZTK5AdYwyNYZD8qNSsqaNj4-aymDXnx55aVkRNcffCL9sZDaNIQPWbHPd6_xQR0OUHiNnLVN8T_Q7NvMUmwrLIklpPq_wCBQ-fWPL4Gh_7Z-QlGlmuonrmkR71UIFd1HHWO264qI6_tuGvtsTooc7NfGZHP88I94VSseUjy1Mo4AMQI4a4ZwK24AmOvGLyAALDFXZ8piwbvBNjU5Bp1zlfoiysiEVcIAok43EhZ1NE2yJptFPu0xManX-q7zijSWLVm07sq77HET6qI-pj7ovHs_xt9Pz7wdUASdVicKSQdOWd4Wm03Iv5pRXipz-9Vok4H_bDtVp079i9IiKpEVNzvqRVjsAgHjtwt9FOi4m2-TfXxYFO0Eqa9ZMKfOuUTPDAN9tFyJuT1e567oLQoM2IZ83wDaQG5OIWnUqopgN7Xh31xWnehL8LvRdLIK8h_y_q-NBZwWDWsogin-gDwvLemMiaEu-x9cFKhzSYfpsSh-p7L5lydtZdnjd48epFpcr6TgpypM2W_mJ1DZQQVdWVKPFYKIQjFLYSY9R7ijuImvxe2qmFIwVhPvFHbZ2LTDQdIFmfsRebImweL0frU4yaxUTbcAMXKGxbjG-DysndDAvG3ziphJA_qWC8T3RBSc_PsHlQee-SX-5SnggC68Gjpab3XHTklQRudW4TUKU3O7jT4rtbnqLACX5wz5LeY0osvBubxecL-KaegGa9oxyK_etejVz53b3tkeMD0gxWeyywraSgZrLTyeQR0FZIKIBpPelc5-FYD1B0yv63enGVy2EsQRIXiy22ta-5wm_nD2p1U67PziDXMigYHjQ5_xj72HGcLLVd5WUHVVuAmTZ0nV-GNp2E-1scwKPYlGth8HJtFPTD5AFd4YqZw0J0pqmVWTU0lSYxqp5-WQqL8bvIhtq8PeZRXfeJ07nW-EocqE_VLGQzMs9TLyA5wh6x=w1920-h991" alt="Work Solution" width="100">
                        <h2 style="color: #007bff;">Work Solution</h2>
                    </div>
                    <p>Estimado usuario,</p>
                    <p>Has solicitado la recuperación de tu contraseña. Si no has sido tú, por favor ignora este correo.</p>
                    <p><strong>Tu contraseña es:</strong> {decrypt(data[0][3])}</p>
                    <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                    <p>Saludos,<br>El equipo de <strong>Work Solution</strong></p>
                </div>
            </body>
            </html>
            """
        msg = Message('Recuperación de contraseña', recipients=[email])
        msg.html = html_body 
        mail.send(msg)

        flash('Correo enviado', 'success')
        return redirect(url_for("login"))
    else:
        flash('Correo no registrado', 'error')
        return redirect(url_for("signup"))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/upload', methods=['POST'])
def upload_file():
    name = request.form.get('name')

    if 'file' not in request.files:
        flash('No se encontró el archivo', 'error')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('index'))

    if name:
        name += "." + file.filename.split('.')[-1]

    if file and allowed_file(file.filename):
        filepath = os.path.join(
            app.config['UPLOAD_FOLDER'], rename_duplicates(name or file.filename))
        file.save(filepath)
        flash('Archivo subido exitosamente', 'success')
        return redirect(url_for('index'))

    flash('Archivo no válido', 'error')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=1000)
