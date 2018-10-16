import random
from flask import Flask, request, redirect, render_template, session, flash
import cgi
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ChemSkills:4LCProject3@localhost:8889/ChemSkills'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'yrtsimehc'

class Students(db.Model):
    id = db.Column(db.Integer)
    name = db.Column(db.String(20))
    school_email = db.Column(db.String(60), primary_key=True)
    teacher_email = db.Column(db.String(60))
    password = db.Column(db.String(20))
    ffnI = db.Column(db.Integer)
    ffnC = db.Column(db.Integer)

    def __init__(self,name,school_email,teacher_email,password):
        self.name = name
        self.school_email = school_email
        self.teacher_email = teacher_email
        self.password = password

class Teachers(db.Model):
    id = db.Column(db.Integer)
    name = db.Column(db.String(20))
    email = db.Column(db.String(60), primary_key=True)
    password = db.Column(db.String(20))
    hint = db.Column(db.String(100))

    def __init__(self,name,email,password,hint):
        self.name = name
        self.email = email
        self.password = password
        self.hint = hint

@app.route('/login')
def login():
    email='Nobody@school.net'

    return render_template('login.html',email=email)

@app.route('/register')
def register():
    student_info = [("Name",'name',''), ("School e-mail",'school_email','This will be your username'),("Teacher's e-mail",'teacher_email',''),("Password",'password','Do not share...'), ("Confirm password",'confirm','')]
    teacher_info = [("Name",'name',''), ("School e-mail",'school_email','This will be your username'),("Password",'password','Do not share...'), ("Confirm password",'confirm',''),("Password hint",'hint','')]
    return render_template('register.html', student_info = student_info, teacher_info = teacher_info)

if __name__ == '__main__':
    app.run()