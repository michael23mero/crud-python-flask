from flask import Flask, render_template, request, redirect, send_from_directory, url_for, flash, session
from flaskext.mysql import MySQL
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('PASS')

print(os.path.dirname(os.path.realpath(__file__)))

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = os.environ.get('DB_HOST')
app.config['MYSQL_DATABASE_USER'] = os.environ.get('DB_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ.get('DB_PASS')
app.config['MYSQL_DATABASE_DB'] = os.environ.get('DB_NAME')
mysql.init_app(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route('/src/uploads/<foto>')
def showPhoto(foto):
    return send_from_directory(app.config['CARPETA'], foto)

#INDEX--------
@app.route('/')
def index():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `imagen`")
    datos = cursor.fetchall()
    conn.commit()
    return render_template('index.html', datos = datos)


#AUTH---------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connect().cursor()
        cursor.execute("SELECT username, password FROM `users` WHERE username = '{}' AND password = '{}'".format(username, password))
        result = cursor.fetchone()
        print(result)
        if result != None:
            session['login'] = True
            session['user'] = username
            return redirect('/home')
        else:
            flash('Ups, credenciales no validas')
            return render_template('login.html')
            
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('login')


# CRUD---------
@app.route('/home')
def home():
    if not 'login' in session:
        return redirect('login')
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `imagen`")
    datos = cursor.fetchall()
    conn.commit()
    return render_template('home.html', datos = datos)

@app.route('/create', methods=['POST'])
def create():
    if not 'login' in session:
        return redirect('login')
    else:
        nombre = request.form['name']
        foto = request.files['foto']

        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")
        if foto.filename != '':
            newNamePhoto = tiempo+foto.filename
            foto.save('src/uploads/'+newNamePhoto)

        sql = "INSERT INTO `imagen` (`id`, `name`, `photo`) VALUES (NULL, %s, %s)"
        data = (nombre, newNamePhoto)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        return redirect('/home')

@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `imagen` WHERE id=%s", (id))
    datos = cursor.fetchall()
    conn.commit()
    return render_template('update.html', datos=datos)

@app.route('/update', methods=['POST'])
def update():
    nombre = request.form['name']
    foto = request.files['foto']
    id = request.form['id']

    sql = "UPDATE `imagen` SET `name`= %s WHERE id = %s;"
    data = (nombre, id)
    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    if foto.filename != '':
        newNamePhoto = tiempo+foto.filename
        foto.save('src/uploads/'+newNamePhoto)
        cursor.execute("SELECT photo FROM `imagen` WHERE id=%s", id)
        result = cursor.fetchall()
        os.remove(os.path.join('src/'+app.config['CARPETA'], result[0][0]))
        cursor.execute("UPDATE `imagen` SET photo=%s WHERE id=%s", (newNamePhoto, id))
        conn.commit()
        cursor.execute(sql, data)
        conn.commit()
    return redirect('/home')

@app.route('/delete/<int:id>')
def remove(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT photo FROM `imagen` WHERE id=%s', id)
    result = cursor.fetchall()
    os.remove(os.path.join('src/'+app.config['CARPETA'], result[0][0]))
    cursor.execute('DELETE FROM `imagen` WHERE id = %s', (id))
    conn.commit()
    return redirect('/home')

if __name__ == '__main__':
    app.run(debug = True, port = 5000)