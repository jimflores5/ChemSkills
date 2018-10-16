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

student_info = [("Name",'name',''), ("School e-mail",'school_email','This will be your username'),("Teacher's e-mail",'teacher_email',''),("Password",'password','Do not share...'), ("Confirm password",'confirm','')]
teacher_info = [("Name",'name',''), ("School e-mail",'school_email','This will be your username'),("Password",'password','Do not share...'), ("Confirm password",'confirm',''),("Password hint",'hint','')]

@app.route('/')
def mainindex():

    return render_template('mainindex.html')

@app.route('/login')
def login():

    return render_template('login.html',title='Login to skills practice')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        progress = int(request.form['progress'])
        if progress == 0:
            role = request.form['role']
            progress += 1
            if role == "Teacher":
                info_list = teacher_info
            else:
                info_list = student_info
            return render_template('register.html', title='Register',info_list = info_list, role=role, progress = progress)
        else:
            role = request.form['role']
            name = request.form['name']
            email = request.form['school_email'].lower()
            password = request.form['password']
            confirm = request.form['confirm']
            if password != confirm:
                flash('Passwords do not match', 'error')
                if role == 'Teacher':
                    info_list = teacher_info
                else:
                    info_list = student_info
                return render_template('register.html', title='Register',info_list = info_list, role=role, progress = 2, name=name, email=email)
            if role == 'Teacher':
                new_teacher = Teachers(name,email,password,request.form['hint'])
                db.session.add(new_teacher)
                db.session.commit()
            else: 
                new_student = Students(name,email,request.form['teacher_email'].lower(),password)
                db.session.add(new_student)
                db.session.commit()

            return render_template('mainindex.html', title='Main page', text = "Check DB to see if registration was successful.")

    progress = 0
    return render_template('register.html', title='Register', progress = progress)

if __name__ == '__main__':
    app.run()