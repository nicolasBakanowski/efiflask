from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length, DataRequired
from werkzeug.urls import url_parse
from forms import LoginForm,SignupForm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
app = Flask(__name__)
app.secret_key = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://root:nbaka145236@localhost/manageremploye'
login_manager = LoginManager(app)
login_manager.login_view = "login"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'

class User(db.Model, UserMixin):  
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    
        

    def __repr__(self):
        return f'<User {self.email}>'
  
    def set_password(self, password):
        self.password = generate_password_hash(password)
  
    def check_password(self, password):
        return check_password_hash(self.password, password)
  
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
  
    @staticmethod
    def get_by_id(id):
        return User.query.get(id)
  
    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

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
   return User.get_by_id(int(user_id))







@app.route("/")
def index():
    all_employes = Employe.query.all() 
    return render_template("index.html",employes = all_employes)

# elementos signup
@app.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
    # Comprobamos que no hay ya un usuario con ese email
        user = User.get_by_email(email)
        if user is not None:
            error = f'El email {email} ya está siendo utilizado por otro usuario'
        else:
            # Creamos el usuario y lo guardamos
            user = User(name=name, email=email)
            user.set_password(password)
            user.save()
        # Dejamos al usuario logueado
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
            return redirect(next_page)
    return render_template("signup_form.html", form=form, error=error)
# fin elementos signup

# elementos Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # Si el usuario ya está autenticado no tiene sentido que se vuelva a loguear, por lo que lo redirigimos a la página principal.
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit(): 
        user = User.get_by_email(form.email.data) #si los datos enviados en el formulario son válidos. En ese caso, intentamos recuperar el usuario a partir del email con get_user()
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


if __name__ == '__main__':
  app.run()
db.init_app(app)
 