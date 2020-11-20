from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.secret_key = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://root:pass@localhost/manageremploye'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
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

@app.route("/")
def index():
    all_employes = Employe.query.all() 
    return render_template("index.html", employes = all_employes)

@app.route("/update", methods = ['GET', 'POST'])
def update ():
    if request.method == "POST":
        employe = Employe.query.get(request.form.get('idemploye'))
        employe.name = request.form['name']
        employe.email = request.form['email']
        employe.phone = request.form['phone']
        db.session.commit()
        flash("updated correctamente")
        return redirect(url_for('index'))

@app.route("/insert", methods = ['POST']) 
def insert():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        newemploye = Employe(name, email, phone)
        db.session.add(newemploye)
        db.session.commit()
        flash("empleado  insertado con exito")
        return redirect(url_for('index'))

@app.route("/delete/<id>/",methods= ["GET","POST"])
def delete(id):
    employe = Employe.query.get(id)
    db.session.delete(employe)
    db.session.commit()
    flash("se borro")
    return redirect(url_for("index"))

if __name__== "__main__":
    app.run(debug=True) 
