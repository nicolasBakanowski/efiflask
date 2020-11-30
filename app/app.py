from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length, DataRequired
from models import users, get_user
from werkzeug.urls import url_parse

app = Flask(__name__)
app.secret_key = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://root:root@localhost/manageremploye'
login_manager = LoginManager(app)
login_manager.login_view = "login"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
db = SQLAlchemy(app)


class Employe(db.Model):
    idemploye = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    def __init__(self,name,email,phone ):
        self.name = name
        self.email = email
        self.phone = phone 


@login_manager.user_loader 
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Login')

@app.route("/")
def index():
    all_employes = Employe.query.all() 
    return render_template("index.html",employes = all_employes)

# elementos signup
@app.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    return render_template("signup_form.html")
# fin elementos signup

# elementos Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # Si el usuario ya está autenticado no tiene sentido que se vuelva a loguear, por lo que lo redirigimos a la página principal.
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit(): 
        user = get_user(form.email.data) #si los datos enviados en el formulario son válidos. En ese caso, intentamos recuperar el usuario a partir del email con get_user()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data) #Si existe un usuario con dicho email y la contraseña coincide, procedemos a autenticar al usuario llamando al método login_user
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('login_form.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
# fin elementos Login

@app.route("/update", methods = ['GET', 'POST'])
@login_required
def update ():
    if request.method == "POST":
        employe = Employe.query.get(request.form.get('idemploye'))
        employe.name = request.form['name']
        employe.email = request.form['email']
        employe.phone = request.form['phone']
        db.session.commit()
        flash("Actualizado correctamente")
        return redirect(url_for('index'))

@app.route("/insert", methods = ['POST'])
@login_required 
def insert():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        newemploye = Employe(name, email, phone)
        db.session.add(newemploye)
        db.session.commit()
        flash("Empleado ingresado con exito")
        return redirect(url_for('index'))

@app.route("/delete/<id>/",methods= ["GET","POST"])
@login_required 
def delete(id):
    employe = Employe.query.get(id)
    db.session.delete(employe)
    db.session.commit()
    flash("El trabajador fue borrado con éxito")
    return redirect(url_for("index"))

app.run(debug=True) 
