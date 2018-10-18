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

class Users(db.Model):
    name = db.Column(db.String(20))
    email = db.Column(db.String(60), primary_key=True)
    password = db.Column(db.String(20))
    role = db.Column(db.String(10))

    def __init__(self,name,email,password,role):
        self.name = name
        self.email = email
        self.password = password
        self.role = role

student_info = [("Name",'name','text',''), ("School e-mail",'school_email','email','This will be your username'),("Teacher's e-mail",'teacher_email','email',''),("Password",'password','password','Do not share...'), ("Confirm password",'confirm','password','')]
teacher_info = [("Name",'name','text',''), ("School e-mail",'school_email','email','This will be your username'),("Password",'password','password','Do not share...'), ("Confirm password",'confirm','password',''),("Password hint",'hint','text','')]
#Tuple order = (Input box label, input box name, input box type, placeholder entry)

def checkRegistration(role,password,confirm,email,temail=''):
    errors = [False,False,False] #[Password error,current user,teacher e-mail check]
    if password != confirm:
        errors[0] = True        #Passwords do not match.
    if role == "Student":
        if Students.query.filter_by(school_email=email).first():  #Check current DB for student's email.
            errors[1] = True    #Already registered.
        if not Teachers.query.filter_by(email=temail).first():  #Check DB for teacher's email.
            errors[2] = True    #Teacher e-mail not in DB.
    else:
        if Teachers.query.filter_by(email=email).first():  #Check current DB for teacher's email.
            errors[1] = True    #Already registered.

    return errors

def chooseCompound(type='all'):  #Temporary function.  TODO - import from NamingPractice.py
    if type == 'ionic':
        compound = ("Ionic name","Ionic formula")
    elif type == 'covalent':
        compound = ("Covalent name","Covalent formula")
    else:
        if random.randint(0,5) == 0:   #20% change to select a bimolecular compound.
            compound = ("Covalent name","Covalent formula")
        else: 
            compound = ("Ionic name","Ionic formula")
    return compound

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/')
def mainindex():
    role = session.get('role', None)
    return render_template('mainindex.html',title="Chem Skills Home",role=role)

@app.route('/namingquizmenu', methods=['POST', 'GET'])
def namingquizmenu():
    if request.method == 'POST':
        choice = request.form['choice']
        instructions = ["Provide the name for each of the following compounds","Provide the chemical formula for each of the following"]
        practiceList = []
        numCorrect = 0
        answers = []
        correct = []
        attempt = 0
        if choice == 'ffnionic' or choice == 'nameionic':
            compoundType = 'ionic'
        elif choice == 'allnaming':
            compoundType = 'all'
        else:
            compoundType = 'covalent'
        while len(practiceList) != 10:
            Compound = chooseCompound(compoundType)
            #if Compound not in practiceList:
            practiceList.append(Compound)
        return render_template('namingquiz.html', instructions = instructions, choice = choice, practiceList = practiceList, numCorrect = numCorrect, answers = answers, correct = correct, attempt=attempt)
    
    return render_template('namingquizmenu.html')

@app.route('/namingquiz', methods=['POST', 'GET'])
def namingquiz():
    if request.method == 'POST':
        choice = request.form['choice']
        
        return render_template('namingquiz.html',choice=choice)
    
    return render_template('namingquizmenu.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        user = Users.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            session['role'] = user.role
            return redirect('/')
        elif user and user.password != password:
            flash('Wrong password.', 'error')
        elif not user:
            flash('Incorrect username','error')
        return render_template('login.html',title='Login to skills practice', email=email)

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
            if role == 'Student':
                info_list = student_info
                temail = request.form['teacher_email'].lower()
                errors = checkRegistration(role,password,confirm,email,temail)
            else:
                info_list = teacher_info
                errors = checkRegistration(role,password,confirm,email)
                temail = ''
            if True in errors:
                if errors[0]:
                    flash('Passwords do not match.', 'error')
                if errors[1]:
                    flash('School e-mail already registered.','error')
                if errors[2]:
                    flash("Teacher e-mail not found. Try again, or use NoTeacher@school.edu to register outside of your class.",'error')
                return render_template('register.html', title='Register',info_list = info_list, role=role, progress = 2, name=name, email=email,temail=temail)
            if role == 'Teacher':
                new_teacher = Teachers(name,email,password,request.form['hint'])
                new_user = Users(name,email,password,role)
                db.session.add(new_teacher)
                db.session.add(new_user)
                db.session.commit()
            else: 
                new_student = Students(name,email,request.form['teacher_email'].lower(),password)
                new_user = Users(name,email,password,role)
                db.session.add(new_student)
                db.session.add(new_user)
                db.session.commit()
            session['role'] = role    
            session['email'] = email
            return redirect('/')

    progress = 0
    return render_template('register.html', title='Register', progress = progress)

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

if __name__ == '__main__':
    app.run()