import random
from flask import Flask, request, redirect, render_template, session, flash
import cgi
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
import NamingBlueprints, SigFigsBlueprints
from NamingBlueprints import naming_practice_blueprint
from SigFigsBlueprints import sigfigs_blueprint

app = Flask(__name__)
app.register_blueprint(naming_practice_blueprint)
app.register_blueprint(sigfigs_blueprint)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ChemSkills:4LCProject3@localhost:8889/ChemSkills'
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
app.secret_key = 'yrtsimehc'

class Students(db.Model):
    id = db.Column(db.Integer)
    name = db.Column(db.String(20))
    school_email = db.Column(db.String(60), primary_key=True)
    teacher_email = db.Column(db.String(60))
    password = db.Column(db.String(20))
    sigfigcounting = db.Column(db.Integer)
    sigfigcalcs = db.Column(db.Integer)
    scinotation = db.Column(db.Integer)
    nameionic = db.Column(db.Integer)
    namecovalent = db.Column(db.Integer)
    ffnI = db.Column(db.Integer)
    ffnC = db.Column(db.Integer)
    allnaming = db.Column(db.Integer)

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
    class1 = db.Column(db.String(15))
    class2 = db.Column(db.String(15))
    #students = db.relationship('Students', backref='teacher_email')

    def __init__(self,name,email,password,class1,class2=''):
        self.name = name
        self.email = email
        self.password = password
        self.class1 = class1
        self.class2 = class2

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
teacher_info = [("Name",'name','text',''), ("School e-mail",'school_email','email','This will be your username'),("Password",'password','password','Do not share...'), ("Confirm password",'confirm','password',''),("Class 1",'class1','text',''),("Class 2",'class2','text','Optional')]
#Tuple order = (Input box label, input box name, input box type, placeholder entry)

digits = ['0','1','2','3','4','5','6','7','8','9']
quiz_labels = {'sigfigcounting':'Counting Sig Figs','sigfigcalcs':'Math with Sig Figs','scinotation':'Scientific Notation','nameionic':'Naming Ionic Compounds','namecovalent':'Naming Covalent Compounds','ffnI':'Formulas From Names (Ionic)','ffnC':'Formulas From Names (Covalent)','allnaming':'Practice All Naming'}
#Dictionary key,value = Quiz menu label : Full skill name

student_DB_headings = ['ID','Name','School_email','Teacher_email','Password','SigFigCounting','SigFigCalcs','SciNotation','Nameionic','Namecovalent','FFNI','FFNC', 'AllNaming']
student_display_data = ['sigfigcounting','sigfigcalcs','scinotation','nameionic','namecovalent','ffnI','ffnC','allnaming']  #Database field names.
student_display_headings = ['Counting Sig Figs','Math with Sig Figs','Scientific Notation','Naming Ionic Compounds','Naming Covalent Compounds','Formulas from Names (Ionic)','Formulas from Names (Covalent)','Practice All Naming']  #Column names to display on User Info page.

def extractData(row):
    all_info = {}
    data = []
    for column in row.__table__.columns:
        all_info[column.name] = str(getattr(row, column.name))
    for item in all_info:
        if item in student_display_data:
            data.append(all_info.get(item))
    return data

def extractScore(user,skill):
    all_info = {}
    for column in user.__table__.columns:
        all_info[column.name] = str(getattr(user, column.name))
    for item in all_info:
        if item == skill:
            try:
                score = Decimal(all_info.get(item))
            except:
                score = 0.0
    return score

def updateDBscores(student,header,new_value):
    Students.query.filter_by(id=student.id).update({header: new_value}) #THIS IS IMPORTANT!!!!  Took 2 hours to find this onine.  It updates a single entry in a DB row when the field name varies each instance.
    db.session.commit()
    return

def determineRank(score):
    numQuestions = session.get('numQuestions',None)
    if numQuestions == 20:
        benchmarks = [90, 75, 60]
    else:
        benchmarks = [90, 70, 50]
    if score < benchmarks[2]:
        rank = "Minimal"
    elif score < benchmarks[1]:
        rank = "Basic"
    elif score < benchmarks[0]:
        rank = "Proficient"
    else:
        rank = "MASTERY" 
    return rank

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

def chooseQuizNumbers(operation):   #'operation': 0 = +, 1 = -, 2 = *, 3 = /.
    operators = ['+', '-', 'x', '/']
    values = []
    flip = False
    if operation < 2:               #For + and -, create 2 values between 0.001 and 90 with 1 - 5 sig figs.
        while len(values) < 2:
            sigFigs = random.randrange(1,6)
            power = random.randrange(-3,2)
            value = SigFigsBlueprints.MakeNumber(sigFigs,power)
            if not SigFigsBlueprints.CheckRounding(value,sigFigs):
                values.append((value,sigFigs))
        print(values)
    else:                           #For * and /, create 2 values between 0.01 and 900 with 1 - 5 sig figs.
        while len(values) < 2:
            sigFigs = random.randrange(1,6)
            power = random.randrange(-2,3)
            value = SigFigsBlueprints.MakeNumber(sigFigs,power)
            values.append((value,sigFigs))
    if operation == 0:              #Validate numbers to avoid ambiguous results.
        if (float(values[0][0])>=10 and values[0][0].find('.') == -1 and values[0][1] < len(values[0][0])) or (float(values[1][0])>=10 and values[1][0].find('.') == -1 and values[1][1] < len(values[1][0])):
            result = SigFigsBlueprints.addWithPlaceholders(values[0][0],values[1][0])
        else:
            result = SigFigsBlueprints.addValues(values[0][0],values[1][0])
    elif operation == 1 and float(values[0][0]) > float(values[1][0]):
        if (float(values[0][0])>=10 and values[0][0].find('.') == -1 and values[0][1] < len(values[0][0])) or (float(values[1][0])>=10 and values[1][0].find('.') == -1 and values[1][1] < len(values[1][0])):
            result = SigFigsBlueprints.subtractWithPlaceholders(values[0][0],values[1][0])
        else:
            result = SigFigsBlueprints.subtractValues(values[0][0],values[1][0])
    elif operation == 1 and float(values[0][0]) < float(values[1][0]):
        flip = True
        if (float(values[0][0])>=10 and values[0][0].find('.') == -1 and values[0][1] < len(values[0][0])) or (float(values[1][0])>=10 and values[1][0].find('.') == -1 and values[1][1] < len(values[1][0])):
            result = SigFigsBlueprints.subtractWithPlaceholders(values[1][0],values[0][0])
        else:
            result = SigFigsBlueprints.subtractValues(values[1][0],values[0][0])
    elif operation == 2:
        result = SigFigsBlueprints.multiplyValues(values[0][0],values[0][1],values[1][0],values[1][1])
    elif float(values[0][0])/float(values[1][0])<1e-4:
        flip = True
        result = SigFigsBlueprints.divideValues(values[1][0],values[1][1],values[0][0],values[0][1])
    else:
        result = SigFigsBlueprints.divideValues(values[0][0],values[0][1],values[1][0],values[1][1])
    if flip:
        pair = (values[1][0],values[0][0],operators[operation],result)
    else:
        pair = (values[0][0],values[1][0],operators[operation],result)

    return pair         #Return a tuple holding the 2 valid numbers, the mathematical operation symbol and the correct answer.
        

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/')
def mainindex():
    role = session.get('role', None)
    return render_template('mainindex.html',title="Chem Skills Home",role=role)

@app.route('/namingquizmenu')
def namingquizmenu():    
    numQuestions = 0
    numCorrect = 0
    session['numQuestions'] = numQuestions
    session['numCorrect'] = numCorrect
    session['listAttempt'] = 0
    return render_template('namingquizmenu.html')

@app.route('/namingquiz', methods=['POST', 'GET'])
def namingquiz():
    if request.method == 'POST':
        choice = request.form['choice']
        if choice == 'ffnI' or choice == 'ffnC':
            title = "Formulas From Names"
        elif choice == 'allnaming':
            title = "Practice All Naming"
        else:
            title = "Names From Formulas"
        session['choice'] = choice
        instructions = ["Provide the name for each of the following compounds","Provide the chemical formula for each of the following", "Provide the formula or name for each of the following compounds"]
        listAttempt = int(session.get('listAttempt',None)) + 1
        if listAttempt == 1:
            practiceList = []
            answers = []
            correct = []
            session['numCorrect'] = 0
            if choice == 'allnaming':
                numQuestions = 20
            else:
                numQuestions = 10
            if choice == 'ffnI' or choice == 'nameionic':
                compoundType = 'ionic'
            elif choice == 'allnaming':
                compoundType = 'all'
            else:
                compoundType = 'molecular'
            while len(practiceList) != numQuestions:
                Compound = NamingBlueprints.chooseCompound(compoundType)
                if Compound not in practiceList:
                    practiceList.append(Compound)
            session['numQuestions'] = numQuestions
            session['listAttempt'] = listAttempt
            return render_template('namingquiz.html', title=title, instructions = instructions, choice = choice, practiceList = practiceList, numCorrect = 0, tally = 0, answers = answers, correct = correct, listAttempt = listAttempt, digits = digits, numQuestions = numQuestions)
        else:
            numQuestions = session.get('numQuestions', None)
            answers = []
            practiceList = []
            tally = 0
            correct = []
            numCorrect = session.get('numCorrect',None)
            for item in range(numQuestions):
                try:        #Excecute 'except' if student tries to refresh browser before first check of answers.
                    answers.append(request.form['answer'+str(item)])
                except:
                    return redirect('/namingquizmenu')      
                Compound = (request.form['name'+str(item)],request.form['formula'+str(item)])
                practiceList.append(Compound)
                if choice == 'ffnI' or choice == 'ffnC' or item > 9:
                    if answers[item] == Compound[1]:
                        flash(':-)', 'correct')
                        if listAttempt == 2:
                            numCorrect += 1
                        tally += 1
                        correct.append(True)
                    else:
                        flash('X', 'error')
                        correct.append(False)
                else:
                    if NamingBlueprints.checkName(answers[item],practiceList[item][0]):
                        flash(':-)', 'correct')
                        if listAttempt == 2:
                            numCorrect += 1
                        tally += 1
                        correct.append(True)
                    else:
                        flash('X', 'error')
                        correct.append(False)
            session['numCorrect'] = numCorrect
            session['listAttempt'] = listAttempt
            numQuestions = session.get('numQuestions',None)
            ratioCorrect = round(Decimal(numCorrect/numQuestions*100),1)
            return render_template('namingquiz.html', title=title, instructions = instructions, choice = choice, practiceList = practiceList, numCorrect = numCorrect, tally=tally, answers = answers, correct = correct, listAttempt = listAttempt, numQuestions = numQuestions, ratioCorrect = ratioCorrect, digits = digits)
    
    return redirect('/namingquizmenu')

@app.route('/sfquiz', methods=['POST', 'GET'])
def sfquiz():
    if request.method == 'POST':
        practiceList = []
        answers = []
        correct = []
        exponents = []
        choice = request.form['choice']
        if choice == 'sigfigcounting':
            title = "Counting & Rounding with Sig Figs"
        elif choice == 'scinotation':
            title = "Scientific Notation"
        else:
            title = "Math with Sig Figs"
        session['choice'] = choice
        instructions = [('Identify the number of sig figs in each of the following','Round each of the followng to the specified number of sig figs'),
        ('Convert to scientific notation','Convert to standard notation'),
        ('Calculate and round the answers to the correct number of sig figs','Calculate and round the answers to the correct number of sig figs')]
        listAttempt = int(session.get('listAttempt',None)) + 1
        if listAttempt == 1:  #Establish initial list of values to present to user
            session['numCorrect'] = 0
            numQuestions = 10
            if choice == 'sigfigcounting':
                while len(practiceList) < 10:
                    if len(practiceList) < 5:       #Generate 5 random numbers having 1 - 6 sig figs.
                        sigFigs = random.randrange(1,7)
                        power = random.randrange(-5,9)
                        value = SigFigsBlueprints.MakeNumber(sigFigs,power)
                        practiceList.append((value,sigFigs))
                    else:
                        iffyValue = True
                        while iffyValue:            #Start with a value that has 8 sig figs and ask the user to round it to 1 - 5 sig figs.
                            sigFigs = random.randrange(1,6)
                            power = random.randrange(-4,6)
                            origValue = SigFigsBlueprints.MakeNumber(8,power)
                            correctAnswer = SigFigsBlueprints.RoundValue(origValue, sigFigs)
                            iffyValue = SigFigsBlueprints.CheckRounding(correctAnswer,sigFigs)
                            value = (origValue,correctAnswer,sigFigs)
                        practiceList.append(value)
            elif choice == 'scinotation':
                while len(practiceList) < numQuestions:  #Generate 10 random numbers listed in standard and scientific notation.
                    sigFigs = random.randrange(1,5)
                    power = random.randrange(-5,7)
                    standard = SigFigsBlueprints.MakeNumber(sigFigs,power)
                    sciDecimal = SigFigsBlueprints.ApplySciNotation(standard, sigFigs)
                    value = (standard,sciDecimal,power)
                    practiceList.append(value)
            else:
                while len(practiceList) < numQuestions:    #Build 10 simple math problems using randomly chosen operators and values.
                    if len(practiceList) < 5:
                        operation = random.randrange(2)    #Randomly select '+' (0) or '-' (1).
                    else:
                        operation = random.randrange(2)+2    #Randomly select '*' (2) or '/' (3).
                    question_params = chooseQuizNumbers(operation)
                    practiceList.append(question_params)
            session['numQuestions'] = numQuestions
            session['listAttempt'] = listAttempt
            return render_template('sfquiz.html', title=title, instructions = instructions, choice = choice, practiceList = practiceList, numCorrect = 0, tally = 0, answers = answers, correct = correct, listAttempt = listAttempt, numQuestions = numQuestions, exponents = exponents)
        
        else:           #Retrieve and check answers.
            try:        #Excecute 'except' if student tries to refresh browser before first check of answers.
                request.form['answer0']
            except:
                return redirect('/sfquiz')
            numQuestions = int(session.get('numQuestions', None))
            numCorrect = int(session.get('numCorrect',None))
            tally = 0
            for item in range(numQuestions): 
                answers.append(request.form['answer'+str(item)])
                if choice == 'sigfigcounting' and item < 5:
                    value = request.form['value'+str(item)]
                    correctAnswer = request.form['sigFigs'+str(item)]
                    practiceList.append((value,correctAnswer))
                elif choice == 'sigfigcounting' and item >= 5:
                    origValue = request.form['origValue'+str(item)]
                    correctAnswer = request.form['correctAnswer'+str(item)]
                    sigFigs = request.form['sigFigs'+str(item)]
                    practiceList.append((origValue,correctAnswer,sigFigs))
                elif choice == 'scinotation':
                    standard = request.form['standard'+str(item)]
                    sciDecimal = request.form['sciDecimal'+str(item)]
                    power = request.form['power'+str(item)]
                    practiceList.append((standard,sciDecimal,power))
                    if item < 5:
                        exponents.append(request.form['exponent'+str(item)])
                        answer = (answers[item],exponents[item])
                        correctAnswer = (sciDecimal,power)
                    else:
                        correctAnswer = standard
                else:
                    firstNum = request.form['firstNum'+str(item)]
                    secondNum = request.form['secondNum'+str(item)]
                    operation = request.form['operation'+str(item)]
                    correctAnswer = request.form['result'+str(item)]
                    practiceList.append((firstNum,secondNum,operation,correctAnswer))

                if (choice == 'sigfigcounting' and (item < 5 and answers[item] == correctAnswer) or (item >= 5 and SigFigsBlueprints.CheckAnswer(correctAnswer,answers[item]))) or (choice == 'scinotation' and (item < 5 and answer == correctAnswer) or (item >= 5 and answers[item] == correctAnswer)) or (choice == 'sigfigcalcs' and SigFigsBlueprints.CheckAnswer(correctAnswer, answers[item])):
                    flash(':-)', 'correct')
                    if listAttempt == 2:
                        numCorrect += 1
                    tally += 1
                    correct.append(True)
                else:
                    flash('X', 'error')
                    correct.append(False)
            ratioCorrect = round(Decimal(numCorrect/numQuestions*100),1)
            session['numCorrect'] = numCorrect
            session['listAttempt'] = listAttempt
            return render_template('sfquiz.html', title=title, instructions = instructions, choice = choice, practiceList = practiceList, numCorrect = numCorrect, tally=tally, answers = answers, correct = correct, listAttempt = listAttempt, numQuestions = numQuestions, ratioCorrect = ratioCorrect, exponents = exponents)
        
        return render_template('sfquiz.html', title=title, menu = False, instructions = instructions)

    menu = 'True'
    listAttempt = 0
    session['listAttempt'] = listAttempt
    return render_template('sfquiz.html', title='Sig Fig Assessment', menu = menu, listAttempt = listAttempt)

@app.route('/updateprogress', methods=['POST', 'GET'])
def updateprogress():
    if request.method == 'POST':
        new_score = request.form['current_score']
        skill = request.form['skill']
        choice = session.get('choice',None)
        email = session.get('email',None)
        user = Students.query.filter_by(school_email=email).first()
        updateDBscores(user,choice,new_score)
        label_index = student_display_data.index(choice)
        if label_index < 3:
            quiz_menu_choice = 'sfquiz'
        else:
            quiz_menu_choice = 'namingquizmenu'

        return render_template('updateprogress.html', afterUpload = True, skill = skill, quiz_menu_choice = quiz_menu_choice)

    choice = session.get('choice',None)
    email = session.get('email',None)
    for item in quiz_labels:
        if item == choice:
            skill = quiz_labels.get(item)
            user = Students.query.filter_by(school_email=email).first()
            prev_score = extractScore(user,choice)
            old_rank = determineRank(prev_score)
            current_score = round(Decimal(session.get('numCorrect', None)/session.get('numQuestions', None)*100),1)
            rank = determineRank(current_score)
    if current_score > prev_score:
        displayText = 0
    elif current_score == prev_score:
        displayText = 1
    else:
        displayText = 2
    return render_template('updateprogress.html',skill = skill, prev_score = prev_score, current_score = current_score, old_rank = old_rank, rank = rank, displayText = displayText)

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
                new_teacher = Teachers(name,email,password,request.form['class1'],request.form['class2'])
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
    session.clear()
    return redirect('/')

@app.route('/userinfo', methods=['POST', 'GET'])
def userinfo():
    if request.method == 'POST':
        return render_template('userinfo.html')

    email = session.get('email',None)
    who = Users.query.filter_by(email=email).first()
    role = who.role
    if role.lower()== 'teacher':
        user = Teachers.query.filter_by(email=email).first()
        user_data = []
        headings = []
    else:
        user = Students.query.filter_by(school_email=email).first()
        headings = student_display_headings
        user_data = extractData(user)
    return render_template('userinfo.html',user=user,role=role, headings = headings, user_data = user_data)

if __name__ == '__main__':
    app.run()