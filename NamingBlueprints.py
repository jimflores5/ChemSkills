import random
from flask import Flask, request, redirect, render_template, session, flash, Blueprint
import cgi
from decimal import Decimal

naming_practice_blueprint = Blueprint('naming_practice_blueprint',__name__)

PosOneCations = [('Hydrogen','H',1,0), ('Lithium','Li',1,0), ('Sodium','Na',1,0), ('Potassium','K',1,0), ('Rubidium','Rb',1,0), ('Cesium','Cs',1,0), ('Silver','Ag',1,0), ('Copper (I)','Cu',1,0), ('Gold (I)','Au',1,0), ('Gallium (I)','Ga',1,0), ('Indium (I)','In',1,0), ('Ammonium','NH4',1,1)]
PosTwoCations = [('Beryllium','Be',2,0), ('Magnesium','Mg',2,0), ('Calcium','Ca',2,0), ('Strontium','Sr',2,0), ('Barium','Ba',2,0), ('Chromium (II)','Cr',2,0), ('Manganese (II)','Mn',2,0), ('Iron (II)','Fe',2,0), ('Cobalt (II)','Co',2,0), ('Nickel','Ni',2,0), ('Copper (II)','Cu',2,0), ('Zinc','Zn',2,0), ('Cadmium','Cd',2,0), ('Mercury (II)','Hg',2,0), ('Tin (II)','Sn',2,0), ('Lead (II)','Pb',2,0)]
PosThreeCations = [('Scandium','Sc',3,0), ('Titanium (III)','Ti',3,0), ('Vanadium (III)','V',3,0), ('Chromium (III)','Cr',3,0), ('Iron (III)','Fe',3,0), ('Cobalt (III)','Co',3,0), ('Gallium (III)','Ga',3,0), ('Indium (III)','In',3,0), ('Yttrium','Y',3,0), ('Rhodium (III)','Rh',3,0), ('Gold (III)','Au',3,0), ('Aluminum','Al',3,0)]
PosFourCations = [('Tin (IV)','Sn',4,0), ('Lead (IV)','Pb',4,0), ('Titanium (IV)','Ti',4,0), ('Vanadium (IV)','V',4,0), ('Manganese (IV)','Mn',4,0), ('Rhodium (IV)','Rh',4,0), ('Tungsten (IV)','W',4,0), ('Osmium (IV)','Os',4,0)]
MiscCations = [('Vanadium (V)','V',5,0), ('Tungsten (V)','W',5,0), ('Chromium (VI)','Cr',6,0), ('Tungsten (VI)','W',6,0)]
MonatomicAnions = [('fluoride','F',-1,0), ('chloride','Cl',-1,0), ('bromide','Br',-1,0), ('iodide','I',-1,0), ('oxide','O',-2,0), ('sulfide','S',-2,0), ('selenide','Se',-2,0), ('nitride','N',-3,0), ('phosphide','P',-3,0)]
PolyatomicAnions = [('nitrate','NO3',-1,1), ('nitrite','NO2',-1,1), ('hydroxide','OH',-1,1), ('hypochlorite','ClO',-1,1), ('chlorite','ClO2',-1,1), ('chlorate','ClO3',-1,1), ('perchlorate','ClO4',-1,1), ('permanganate','MnO4',-1,1), ('acetate','C2H3O2',-1,1), ('cyanide','CN',-1,1), ('hydrogen carbonate','HCO3',-1,1), ('hydrogen sulfate','HSO4',-1,1), ('dihydrogen phosphate','H2PO4',-1,1), ('sulfate','SO4',-2,1), ('sulfite','SO3',-2,1), ('carbonate','CO3',-2,1), ('chromate','CrO4',-2,1), ('dichromate','Cr2O7',-2,1), ('hydrogen phosphate','HPO4',-2,1), ('oxalate','C2O4',-2,1), ('phosphate','PO4',-3,1), ('phosphite','PO3',-3,1)]
# Ion tuple order = (Ion name, forumla, charge, monatomic/polyatomic ID 0/1 = No/Yes)

BimolecularCpds = [('Diboron hexachloride','B2Cl6',0), ('Dibromine monoxide','Br2O','Dibromine monooxide'), ('Bromine trifluoride','BrF3',0), ('Dicarbon dihydride','C2H2','Ethyne'), ('Dicarbon tetrahydride','C2H4','Ethene'), ('Dicarbon hexahydride','C2H6','Ethane'), ('Tricarbon tetrahydride','C3H4','Propyne'), ('Tricarbon hexahydride','C3H6','Propene'), ('Tricarbon octahydride','C3H8','Propane'), ('Tetracarbon decahydride','C4H10','Butane'), ('Tetracarbon hexahydride','C4H6','Butyne'), ('Tetracarbon octahydride','C4H8','Butene'), ('Pentacarbon decahydride','C5H10','Pentene'), ('Pentacarbon octahydride','C5H8','Pentyne'), ('Carbon tetrachloride','CCl4',0), ('Dicarbon hexachloride','C2Cl6',0), ('Carbon tetrahydride','CH4','Methane'), ('Dichlorine monoxide','Cl2O','Dichlorine monooxide'), ('Carbon monoxide','CO','Carbon monooxide'), ('Carbon dioxide','CO2',0), ('Dihydrogen monoxide','H2O','Water'), ('Diiodine tetroxide','I2O4','Diiodine tetraoxide'), ('Diiodine pentoxide','I2O5','Diiodine pentaoxide'), ('Iodine monobromide','IBr',0), ('Dinitrogen monoxide','N2O','Dinitrogen monooxide'), ('Dinitrogen tetroxide','N2O4','Dinitrogen tetraoxide'), ('Nitrogen trihydride','NH3','Ammonia'), ('Nitrogen tribromide','NBr3',0), ('Nitrogen monoxide','NO','Nitrogen monooxide'), ('Nitrogen dioxide','NO2',0), ('Diphosphorous tetrabromide','P2Br4',0), ('Tetraphosphorous decoxide','P4O10','Tetraphosphorous decaoxide'), ('Phosphorous pentachloride','PCl5',0), ('Phosphorous trifluoride','PF3',0), ('Phosphouous trihydride','PH3',0), ('Sulfur difluoride','SF2',0), ('Sulfur hexafluoride','SF6',0), ('Sulfur dioxide','SO2',0), ('Sulfur trioxide','SO3',0)]
# Molecular tuple order = (Name, forumla, alternate name (0 if none))

cations = PosOneCations+PosTwoCations+PosThreeCations+PosFourCations+MiscCations
anions = MonatomicAnions+PolyatomicAnions
digits = ['0','1','2','3','4','5','6','7','8','9']

def chooseCompound(type='all'):
    oopsHH = True
    if type == 'molecular':
        choice = random.choice(BimolecularCpds)
        compound = (choice[0],choice[1]) #compound = (name, formula)
    elif type == 'ionic':
        while oopsHH:               #Prevent formulas starting with 'HH', and prevent calling 'H2O' ionic.
            cation = random.choice(cations)
            anion = random.choice(anions)
            name = cation[0] + ' ' + anion[0]
            formula = findSubscripts(cation,anion)
            compound = (name, formula)
            if cation[1] != anion[1][0] and formula != "H2O" and formula != "HOH":
                oopsHH = False
    else:
        if random.randint(0,5) == 0:   #20% change to select a bimolecular compound.
            choice = random.choice(BimolecularCpds)
            compound = (choice[0],choice[1])
        else:                           #80% change to select an ionic compound.
            while oopsHH:
                cation = random.choice(cations)
                anion = random.choice(anions)
                name = cation[0] + ' ' + anion[0]
                formula = findSubscripts(cation,anion)
                compound = (name, formula)
                if cation[1] != anion[1][0] and formula != "H2O" and formula != "HOH":
                    oopsHH = False
    return compound

def findSubscripts(cation, anion):  #Idenfity the formula for an ionic compound.  Add '()' around polyatomic ions, if needed.
    if cation[2] == -anion[2]:
        formula = cation[1]+anion[1]
    elif cation[2] < -anion[2] and -anion[2]%cation[2]==0:
        if cation[3]:
            formula = "({0}){1}{2}".format(cation[1],str(int(-anion[2]/cation[2])),anion[1]) 
        else:
            formula = cation[1]+str(int(-anion[2]/cation[2]))+anion[1]
    elif cation[2] > -anion[2] and -cation[2]%anion[2]==0:
        if anion[3]:
            formula = "{0}({1}){2}".format(cation[1],anion[1],str(int(-cation[2]/anion[2]))) 
        else:
            formula = cation[1]+anion[1]+str(int(-cation[2]/anion[2]))
    else:
        if cation[3]:
            formula = "({0}){1}".format(cation[1],str(-anion[2]))
        else:
            formula = cation[1]+str(-anion[2])
        if anion[3]:
            formula += "({0}){1}".format(anion[1],str(cation[2]))
        else:
            formula += anion[1]+str(cation[2])
    return formula

def checkName(answer,name):
    if any(name in code for code in BimolecularCpds):  #If the compound is molecular, check for alternate names.
        index = [x for x, y in enumerate(BimolecularCpds) if y[0] == name]
        choice = BimolecularCpds[index[0]]
        name = name.replace(' ','')
        answer = answer.replace(' ','')
        if choice[2] != 0:
            altname = choice[2].replace(' ','')
            if answer.lower() == name.lower() or answer.lower() == altname.lower():
                result = True
            else:
                result = False
        else:
            if answer.lower() == name.lower():
                result = True
            else:
                result = False
    else:
        if 'bicarbonate' in answer.lower() or 'bisulfate' in answer.lower():    #Correct for alterante names for HCO3- and HSO4-.
            answer = answer.lower()
            answer = answer.replace('bi','hydrogen ')
        answer = answer.replace(' ','')
        name = name.replace(' ','')
        if answer.lower() == name.lower():
            result = True
        else:
            result = False
    return result

def checkResponse(response,displayText):
    answers = [('2-','-2'),'3',('6-','-6'),('6+','+6'),('3+','+3')]
    responseNumber = displayText - 10
    print(displayText, responseNumber, answers[responseNumber], response)
    if responseNumber != 1 and ('+' not in response and '-' not in response) and response != '?':
        return 'sign'
    if (response == '?' or response in answers[responseNumber]) and response != '':
        return True
    else:
        return False


@naming_practice_blueprint.route('/namingindex')
def namingindex():
    nameAttempts = 0
    nameCorrect = 0
    formAttempts = 0
    formCorrect = 0
    session['nameAttempts'] = nameAttempts
    session['nameCorrect'] = nameCorrect
    session['formAttempts'] = formAttempts
    session['formCorrect'] = formCorrect
    return render_template('namingindex.html',title="Naming Practice")

@naming_practice_blueprint.route('/namesfromformulas/<type>',methods=['POST', 'GET'])
def namesfromformulas(type):
    if request.method == 'POST':
        nameAttempts = session.get('nameAttempts', None)
        nameCorrect = session.get('nameCorrect', None)
        answer = request.form['answer']
        name = request.form['name']
        formula = request.form['formula']
        firstAttempt = request.form['firstAttempt']
        if checkName(answer,name):
            flash('Correct!  :-)', 'correct')
            if firstAttempt == 'True':
                nameCorrect += 1
                session['nameCorrect'] = nameCorrect
        else:
            flash('Try again, or click here to reveal the answer.', 'error')

        ratioCorrect = round(Decimal(nameCorrect/nameAttempts*100),1)
        return render_template('namesfromformulas.html', title="Names fron Formulas", name = name, formula = formula, answer = answer, digits = digits, type = type, nameAttempts = nameAttempts, nameCorrect = nameCorrect, firstAttempt = False, ratioCorrect = ratioCorrect)
    
    nameAttempts = session.get('nameAttempts', None) + 1
    nameCorrect = session.get('nameCorrect', None)
    session['nameAttempts'] = nameAttempts
    ratioCorrect = round(Decimal(nameCorrect/nameAttempts*100),1)
    Compound = chooseCompound(type)
    return render_template('namesfromformulas.html',title="Names fron Formulas", name = Compound[0], formula = Compound[1], digits = digits, type = type, nameAttempts = nameAttempts, nameCorrect = nameCorrect, firstAttempt = True, ratioCorrect = ratioCorrect)

@naming_practice_blueprint.route('/formulasfromnames/<type>',methods=['POST', 'GET'])
def formulasfromnames(type):
    if request.method == 'POST':
        formAttempts = session.get('formAttempts', None)
        formCorrect = session.get('formCorrect', None)
        firstAttempt = request.form['firstAttempt']
        answer = request.form['answer']
        name = request.form['name']
        formula = request.form['formula']
        if answer == formula:
            flash('Correct!  :-)', 'correct')
            correct = True
            if firstAttempt == 'True':
                formCorrect += 1
                session['formCorrect'] = formCorrect
        else:
            flash('Try again, or click here to reveal the answer.', 'error')
            correct = False

        ratioCorrect = round(Decimal(formCorrect/formAttempts*100),1)
        return render_template('formulasfromnames.html', title="Formulas from Names", name = name, formula = formula, answer = answer, digits = digits, type = type, formAttempts = formAttempts, formCorrect = formCorrect, firstAttempt = False, ratioCorrect = ratioCorrect, correct=correct)

    formAttempts = session.get('formAttempts', None) + 1
    formCorrect = session.get('formCorrect', None)
    session['formAttempts'] = formAttempts
    ratioCorrect = round(Decimal(formCorrect/formAttempts*100),1)
    Compound = chooseCompound(type)
    return render_template('formulasfromnames.html',title="Formulas from Names", name = Compound[0], formula = Compound[1], digits = digits, type = type, formAttempts = formAttempts, formCorrect = formCorrect, firstAttempt = True, ratioCorrect = ratioCorrect, correct = False)

@naming_practice_blueprint.route('/allnaming',methods=['POST', 'GET'])
def allnaming():
    if request.method == 'POST':
        nameAttempts = session.get('nameAttempts', None)
        nameCorrect = session.get('nameCorrect', None)
        formAttempts = session.get('formAttempts', None)
        formCorrect = session.get('formCorrect', None)
        firstAttempt = request.form['firstAttempt']
        answer = request.form['answer']
        name = request.form['name']
        formula = request.form['formula']
        question = request.form['question']
        if question == '0' and checkName(answer,name):
            flash('Correct!  :-)', 'correct')
            correct = True
            if firstAttempt == 'True':
                nameCorrect += 1
                session['nameCorrect'] = nameCorrect
        elif question == '1' and answer == formula:
            flash('Correct!  :-)', 'correct')
            correct = True
            if firstAttempt == 'True':
                formCorrect += 1
                session['formCorrect'] = formCorrect
        else:
            flash('Try again, or click here to reveal the answer.', 'error')
            correct = False
    
        return render_template('allnaming.html', title="Practice All Naming", name = name, formula = formula, answer = answer, digits = digits, question = question, nameAttempts = nameAttempts, nameCorrect = nameCorrect, formAttempts = formAttempts, formCorrect = formCorrect, firstAttempt = False, correct = correct)

    Compound = chooseCompound()
    question = str(random.randint(0,1))
    nameCorrect = session.get('nameCorrect', None)
    formCorrect = session.get('formCorrect', None)
    nameAttempts = session.get('nameAttempts', None)
    formAttempts = session.get('formAttempts', None)
    if question == '0':
        nameAttempts = session.get('nameAttempts', None) + 1
        session['nameAttempts'] = nameAttempts
        session['formAttempts'] = formAttempts
    else:
        formAttempts = session.get('formAttempts', None) + 1
        session['formAttempts'] = formAttempts
        session['nameAttempts'] = nameAttempts
    return render_template('allnaming.html',title="Practice All Naming", name = Compound[0], formula = Compound[1], digits = digits, question = question, nameAttempts = nameAttempts, nameCorrect = nameCorrect, formAttempts = formAttempts, formCorrect = formCorrect, firstAttempt = True)

@naming_practice_blueprint.route('/ionicnamingtutorial/<type>',methods=['POST', 'GET'])
def ionicnamingtutorial(type):
    if request.method == 'POST':
        page = int(request.form['page'])
        displayText = int(request.form['displayText'])+1
        if page == 3 or page == 5:
            answers = []
            practiceList = []
            numCorrect = 0
            for item in range(4):
                answers.append(request.form['answer'+str(item)])
                Compound = (request.form['name'+str(item)],request.form['formula'+str(item)])
                practiceList.append(Compound)
                if checkName(answers[item],practiceList[item][0]):
                    flash('Correct!  :-)', 'correct')
                    numCorrect += 1
                else:
                    flash('Try again, or click here to reveal the answer.', 'error')
            return render_template('ionicnamingtutorial.html', title="Naming Ionic Compounds", page = page, displayText = displayText, practiceList = practiceList, digits = digits, answers = answers, numCorrect = numCorrect)

        elif page == 4:
            response = ''
            if displayText > 9 and displayText <= 14:
                response = request.form['response']
                if checkResponse(response,displayText) == 'sign':
                    flash('Be sure to include the sign (+/-) in addition to the number.', 'error')
                    displayText -= 1
                elif checkResponse(response,displayText):
                    imageName = 'RomanNumerals'+str(displayText)+'.png'
                    response = ''
                else:
                    flash("Try again, or submit '?' to see the answer.", 'error')
                    displayText -= 1

            imageName = 'RomanNumerals'+str(displayText)+'.png'
            
            return render_template('ionicnamingtutorial.html', title="Naming Ionic Compounds", page = page, displayText = displayText, imageName = imageName, response = response)

        return render_template('ionicnamingtutorial.html', title="Naming Ionic Compounds", page = page, displayText = displayText)
    
    displayText = 1
    page = int(type)
    if page == 3 or page == 5:
        practiceList = []
        answers = []
        numCorrect = 0
        while len(practiceList) != 4:
            Compound = chooseCompound('ionic')
            if ((page == 3 and "(" not in Compound[0]) or (page == 5 and "(" in Compound[0])) and Compound not in practiceList:
                practiceList.append(Compound)

        return render_template('ionicnamingtutorial.html',title="Naming Ionic Compounds", page = page, displayText = displayText, practiceList = practiceList, digits = digits, answers = answers, numCorrect = numCorrect)
    
    elif page == 4:
        imageName = 'RomanNumerals'+str(displayText)+'.png'
        return render_template('ionicnamingtutorial.html', title="Naming Ionic Compounds", page = page, displayText = displayText, imageName = imageName)
    
    return render_template('ionicnamingtutorial.html',title="Naming Ionic Compounds", page = page, displayText = displayText)

@naming_practice_blueprint.route('/IDthemetals',methods=['POST', 'GET'])
def IDthemetals():
    if request.method == 'POST':
        page = int(request.form['page'])
        displayImage = int(request.form['displayImage'])+1
        if displayImage <= 2:
            return render_template('idthemetals.html', title="Naming Ionic Compounds", page = page, displayImage = displayImage)
        else:
            return render_template('ionicnamingtutorial.html', title="Naming Ionic Compounds", page = page, displayText = 3)
    
    displayImage = 1
    page = 1
    return render_template('idthemetals.html',title="Naming Ionic Compounds", page = page, displayImage = displayImage)

@naming_practice_blueprint.route('/idpolyatomics',methods=['POST', 'GET'])
def idpolyatomics():
    if request.method == 'POST':
        page = int(request.form['page'])
        answers = []
        practiceList = []
        numCorrect = 0
        correctAns = []
        if request.form['done'] == '1':
            return render_template('ionicnamingtutorial.html',title="Naming Ionic Compounds", page = page, displayText = 4)
            
        for item in range(4):
            answers.append(request.form['answer'+str(item)])
            Compound = (request.form['name'+str(item)],request.form['formula'+str(item)])
            practiceList.append(Compound)
            correctAns.append(request.form['correctAns'+str(item)])
            if answers[item] == correctAns[item]:
                flash('Correct!  :-)', 'correct')
                numCorrect += 1
            else:
                flash('Try again', 'error')
        return render_template('idpolyatomics.html', title="Naming Ionic Compounds", page = page, practiceList = practiceList, answers = answers, numCorrect = numCorrect, digits = digits, correctAns = correctAns)

    page = 1
    practiceList = []
    answers = []
    numCorrect = 0
    correctAns = []
    while len(practiceList) != 4:
        Compound = chooseCompound('ionic')
        if Compound not in practiceList:
            practiceList.append(Compound)
            nameParts = Compound[0].split()
            if [entry for entry in PolyatomicAnions if nameParts[-1] in entry]:
                correctAns.append('polyatomic')
            else:
                correctAns.append('monatomic')
    return render_template('idpolyatomics.html',title="Naming Ionic Compounds", page = page, practiceList = practiceList, answers = answers, numCorrect = numCorrect, digits = digits, correctAns = correctAns)

@naming_practice_blueprint.route('/multiplecharges',methods=['POST', 'GET'])
def multiplecharges():
    if request.method == 'POST':
        page = int(request.form['page'])
        if request.form['done'] == '1':
            return render_template('ionicnamingtutorial.html',title="Naming Ionic Compounds", page = page, displayText = 3, imageName = 'RomanNumerals3.png')
        metals = []
        answers = request.form.getlist('answers')
        correctAns = []
        for item in range(4):
            metal = (request.form['symbol'+str(item)],request.form['type'+str(item)])
            metals.append(metal)
            if metal[1] == 'single':
                correctAns.append(metal[0])
        if correctAns == answers:
            flash('Correct!  :-)', 'correct')
            allCorrect = True
        else:
            if len(answers) > len(correctAns):
                flash('Try again (too many boxes checked).' , 'error')
            elif len(answers) < len(correctAns):
                flash('Try again (too few boxes checked).' , 'error')
            else:
                flash('Try again.  Correct number of boxes checked, but incorrect selections.' , 'error')
            allCorrect = False

        return render_template('multiplecharges.html',title="Naming Ionic Compounds", page = page, metals = metals, answers = answers, allCorrect = allCorrect, correctAns = correctAns)
    
    page = 4
    metals = []
    answers = []
    allCorrect = False
    correctAns = []
    while len(metals) != 4:
        cation = random.choice(cations)
        if '(' not in cation[0] and cation[1] != 'NH4':
            metal = (cation[1],'single')
        elif '(' in cation[0] and cation[1] != 'NH4':
            metal = (cation[1],'multiple')
        else:
            metal = ''
        if metal not in metals and metal != '':
            metals.append(metal)
            if metal[1] == 'single':
                correctAns.append(metal[0])
    return render_template('multiplecharges.html',title="Naming Ionic Compounds", page = page, metals = metals, answers = answers, allCorrect = allCorrect, correctAns = correctAns)

@naming_practice_blueprint.route('/covalentnamingtutorial/<type>',methods=['POST', 'GET'])
def covalentnamingtutorial(type):
    if request.method == 'POST':
        page = int(request.form['page'])
        displayText = int(request.form['displayText'])+1
        answers = []
        practiceList = []
        numCorrect = 0
        if page == 1:
            correctAns = []                
            for item in range(4):
                answers.append(request.form['answer'+str(item)])
                Compound = (request.form['name'+str(item)],request.form['formula'+str(item)])
                practiceList.append(Compound)
                correctAns.append(request.form['correctAns'+str(item)])
                if answers[item] == correctAns[item]:
                    flash('Correct!  :-)', 'correct')
                    numCorrect += 1
                else:
                    flash('Try again', 'error')
            return render_template('covalentnamingtutorial.html', title="Naming Covalent Compounds", page = page, displayText = displayText, practiceList = practiceList, answers = answers, numCorrect = numCorrect, digits = digits, correctAns = correctAns)
        else:
            for item in range(4):
                answers.append(request.form['answer'+str(item)])
                Compound = (request.form['name'+str(item)],request.form['formula'+str(item)])
                practiceList.append(Compound)
                if checkName(answers[item],practiceList[item][0]):
                    flash('Correct!  :-)', 'correct')
                    numCorrect += 1
                else:
                    flash('Try again, or click here to reveal the answer.', 'error')
            return render_template('covalentnamingtutorial.html', title="Naming Covalent Compounds", page = page, displayText = displayText, practiceList = practiceList, digits = digits, answers = answers, numCorrect = numCorrect)
        
    displayText = 1
    page = int(type)
    practiceList = []
    answers = []
    numCorrect = 0
    if page == 1:
        correctAns = []
        while len(practiceList) != 4:
            flip = random.randint(0,1)
            if flip == 0:
                Compound = chooseCompound('ionic')
            else:
                Compound = chooseCompound('molecular')
            if Compound not in practiceList and [entry for entry in BimolecularCpds if Compound[0] in entry]:
                practiceList.append(Compound)
                correctAns.append('covalent')
            elif Compound not in practiceList:
                practiceList.append(Compound)
                correctAns.append('ionic')
        print(answers,correctAns)
        return render_template('covalentnamingtutorial.html',title="Naming Covalent Compounds", page = page, displayText = displayText, practiceList = practiceList, digits = digits, answers = answers, numCorrect = numCorrect, correctAns = correctAns)
    else:
        while len(practiceList) != 4:
            Compound = chooseCompound('molecular')
            if Compound not in practiceList:
                practiceList.append(Compound)

        return render_template('covalentnamingtutorial.html',title="Naming Covalent Compounds", page = page, displayText = displayText, practiceList = practiceList, digits = digits, answers = answers, numCorrect = numCorrect)

@naming_practice_blueprint.route('/ffmtutorial/<type>',methods=['POST', 'GET'])
def ffmtutorial(type):
    if request.method == 'POST':
        page = int(request.form['page'])
        answers = []
        practiceList = []
        numCorrect = 0
        correct = []
        for item in range(4):
            answers.append(request.form['answer'+str(item)])
            Compound = (request.form['name'+str(item)],request.form['formula'+str(item)])
            practiceList.append(Compound)
            if answers[item] == Compound[1]:
                flash('Correct!  :-)', 'correct')
                numCorrect += 1
                correct.append(True)
            else:
                flash('Try again, or click here to reveal the answer.', 'error')
                correct.append(False)
        return render_template('ffmtutorial.html', title="Formulas from Names", page = page, practiceList = practiceList, digits = digits, answers = answers, numCorrect = numCorrect, correct = correct)
    
    page = int(type)
    answers = []
    practiceList = []
    numCorrect = 0
    correct = []
    if page == 1:
        compoundType = 'ionic'
    else:
        compoundType = 'molecular'
    while len(practiceList) != 4:
        Compound = chooseCompound(compoundType)
        if Compound not in practiceList:
            practiceList.append(Compound)

    return render_template('ffmtutorial.html',title="Formulas from Names", page = page, practiceList = practiceList, digits = digits, answers = answers, numCorrect = numCorrect, correct = correct)