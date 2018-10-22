import random
from flask import Flask, request, redirect, render_template, session, flash, Blueprint
import cgi
from SigFigFuncs import MakeNumber, RoundValue, CheckAnswer, CheckRounding, ApplySciNotation, addValues, subtractValues, multiplyValues, divideValues, findDecimalPlaces, addWithPlaceholders, subtractWithPlaceholders

sigfigs_blueprint = Blueprint('sigfigs_blueprint',__name__)

@sigfigs_blueprint.route('/sigfigindex')
def sigfigindex():
    return render_template('sigfigindex.html',title="Sig Fig Practice")

@sigfigs_blueprint.route('/countingsf', methods=['POST', 'GET'])
def countingsf():
    if request.method == 'POST':
        answer = request.form['answer']
        actualSigFigs = request.form['actualSigFigs']
        value = request.form['value']
        if answer==actualSigFigs:
            flash('Correct!  :-)', 'correct')
        else:
            flash('Try again, or click here to reveal the answer.', 'error')
        
        return render_template('countingSigFigs.html', value=value, sigFigs = actualSigFigs, answer = answer)

    sigFigs = random.randrange(1,7)
    power = random.randrange(-5,9)
    value = MakeNumber(sigFigs,power)
    return render_template('countingSigFigs.html',title="Counting Sig Figs", value=value, sigFigs = sigFigs)

@sigfigs_blueprint.route('/roundingsf', methods=['POST', 'GET'])
def roundingsf():
    if request.method == 'POST':
        answer = request.form['answer']
        origValue = request.form['value']
        sigFigs = int(request.form['sigFigs'])
        roundedValue = RoundValue(origValue, sigFigs)
        if CheckAnswer(roundedValue, answer):
            flash('Correct!  :-)', 'correct')
        else:
            flash('Try again, or click here to reveal the answer.', 'error')
        
        return render_template('roundingSigFigs.html', value=origValue, sigFigs = sigFigs, answer = answer, roundedValue=roundedValue)
    
    iffyValue = True
    while iffyValue:
        sigFigs = random.randrange(1,7)
        power = random.randrange(-4,6)
        value = MakeNumber(9,power)
        result = RoundValue(value, sigFigs)
        iffyValue = CheckRounding(result,sigFigs)
    
    return render_template('roundingSigFigs.html',title="Rounding Sig Figs", value=value, sigFigs = sigFigs)

@sigfigs_blueprint.route('/sfcalcs', methods=['POST', 'GET'])
def sfcalcs():
    if request.method == 'POST':
        answer = request.form['answer']
        result = request.form['result']
        value1 = request.form['value1']
        value2 = request.form['value2']
        operation = request.form['operation']
        if CheckAnswer(result, answer):
            flash('Correct!  :-)', 'correct')
        else:
            flash('Try again, or click here to reveal the answer.', 'error')
        
        return render_template('sfCalcs.html',title="Calculations with Sig Figs", value1 = value1, value2 = value2, result = result, answer = answer, operation=operation)

    operators = ['+', '-', 'x', '/']
    operation = random.randrange(4) #Randomly select +, -, * or / using integers 0 - 3, respectively.
    if operation < 2:      #For + and -, create 2 values between 0.001 and 90 with 1 - 6 sig figs.
        iffyValue = True
        while iffyValue:
            sigFigs = random.randrange(1,7)
            power = random.randrange(-3,2)
            value = MakeNumber(sigFigs,power)
            iffyValue = CheckRounding(value,sigFigs)
        sigFigs1 = sigFigs
        power1 = power
        value1 = value
        iffyValue = True
        while iffyValue:
            sigFigs = random.randrange(1,7)
            power = random.randrange(-3,2)
            value = MakeNumber(sigFigs,power)
            iffyValue = CheckRounding(value,sigFigs)
        sigFigs2 = sigFigs
        power2 = power
        value2 = value
    else:                   #For * and /, create 2 values between 0.01 and 900 with 1 - 6 sig figs.
        sigFigs1 = random.randrange(1,7)
        power1 = random.randrange(-2,3)
        value1 = MakeNumber(sigFigs1,power1)
        sigFigs2 = random.randrange(1,7)
        power2 = random.randrange(-2,3)
        value2 = MakeNumber(sigFigs2,power2)

    if operation == 0:
        if (float(value1)>=10 and value1.find('.') == -1 and sigFigs1 < len(value1)) or (float(value2)>=10 and value2.find('.') == -1 and sigFigs2 < len(value2)):
            result = addWithPlaceholders(value1,value2)
        else:
            result = addValues(value1,value2)
        return render_template('sfCalcs.html',title="Calculations with Sig Figs", value1 = value1, value2 = value2, operation = operators[operation], result = result)
    elif operation == 1 and value1 > value2:
        if (float(value1)>=10 and value1.find('.') == -1 and sigFigs1 < len(value1)) or (float(value2)>=10 and value2.find('.') == -1 and sigFigs2 < len(value2)):
            result = subtractWithPlaceholders(value1,value2)
        else:
            result = subtractValues(value1,value2)
        return render_template('sfCalcs.html',title="Calculations with Sig Figs", value1 = value1, value2 = value2, operation = operators[operation], result = result)
    elif operation == 1 and float(value1) < float(value2):
        if (float(value1)>=10 and value1.find('.') == -1 and sigFigs1 < len(value1)) or (float(value2)>=10 and value2.find('.') == -1 and sigFigs2 < len(value2)):
            result = subtractWithPlaceholders(value2,value1)
        else:
            result = subtractValues(value2,value1)
        return render_template('sfCalcs.html',title="Calculations with Sig Figs", value1 = value2, value2 = value1, operation = operators[operation], result = result)
    elif operation == 2:
        result = multiplyValues(value1,sigFigs1,value2,sigFigs2)
        return render_template('sfCalcs.html',title="Calculations with Sig Figs", value1 = value1, value2 = value2, operation = operators[operation], result = result)
    elif float(value1)/float(value2)<1e-4:
        result = divideValues(value2,sigFigs2,value1,sigFigs1)
        return render_template('sfCalcs.html',title="Calculations with Sig Figs", value1 = value2, value2 = value1, operation = operators[operation], result = result)
    else:
        result = divideValues(value1,sigFigs1,value2,sigFigs2)
        return render_template('sfCalcs.html',title="Calculations with Sig Figs", value1 = value1, value2 = value2, operation = operators[operation], result = result)

@sigfigs_blueprint.route('/scinotation', methods=['POST', 'GET'])
def scinotation():
    if request.method == 'POST':
        sciNot = request.form['sciNot']
        if sciNot=='True':              #Given a value in sci notation, the user eneters a number in standard notation.
            answer = request.form['answer']
            result = request.form['value']
            sciValue = request.form['sciValue']
            power = request.form['power']
            if CheckAnswer(result, answer):
                flash('Correct!  :-)', 'correct')
            else:
                flash('Try again, or click here to reveal the answer.', 'error')
            return render_template('scientificNotation.html',title="Scientific Notation", value = result, sciValue=sciValue, power = power, sciNot = True, answer = answer)
        else:                            #Given a value in standard notation, the user eneters a number in sci notation.
            answer = request.form['answer']
            result = request.form['value']
            sciValue = request.form['sciValue']
            power = request.form['power']
            exponent = request.form['exponent']
            if CheckAnswer(power, exponent) and CheckAnswer(sciValue,answer):
                flash('Correct!  :-)', 'correct')
            elif CheckAnswer(power, exponent) and not CheckAnswer(sciValue,answer):
                flash('Correct power.  Wrong decimal value.', 'error')
            elif CheckAnswer(sciValue,answer) and not CheckAnswer(power, exponent):
                flash('Correct decimal value.  Wrong power.', 'error')
            else:
                flash('Both entries are incorrect.  Try again, or click to reveal the answer.', 'error')
                
            return render_template('scientificNotation.html',title="Scientific Notation", value = result, sciValue=sciValue, power = power, sciNot = False, answer = answer, exponent = exponent)

    sigFigs = random.randrange(1,5)
    power = random.randrange(-5,9)
    value = MakeNumber(sigFigs,power)
    sciValue = ApplySciNotation(value, sigFigs)
    if random.randrange(2) == 0:  #Flip a coin: If '0', ask the user to change sci notation into standard notation.
        return render_template('scientificNotation.html',title="Scientific Notation", value = value, sciValue=sciValue, power = power, sciNot = True)
    else:                         #Otherwise ('1'), ask the user to change standard notation into sci notation.
        return render_template('scientificNotation.html',title="Scientific Notation", value=value, sciValue=sciValue, power = power, sciNot = False)

@sigfigs_blueprint.route('/sftutorial1', methods=['POST', 'GET'])
def sftutorial1():
    if request.method == 'POST':
        displayText = int(request.form['displayText'])
        displayText += 1
    else:
        displayText=1
    
    return render_template('sftutorial1.html',title="Sig Fig Tutorial", page = 1, displayText=displayText)

@sigfigs_blueprint.route('/sftutorial2', methods=['POST', 'GET'])
def sftutorial2():
    if request.method == 'POST':
        firstZeroRule = request.form['firstZeroRule']
        session['firstZeroRule'] = firstZeroRule
        secondHalf = True
        if firstZeroRule == '':
            flash('Please enter a response.', 'error')
            secondHalf = False
        
        return render_template('sftutorial2.html', answer = firstZeroRule, page = 2, secondHalf = secondHalf)

    return render_template('sftutorial2.html',title="Sig Fig Tutorial", page = 2, secondHalf=False)

@sigfigs_blueprint.route('/sftutorial3', methods=['POST', 'GET'])
def sftutorial3():
    if request.method == 'POST':
        firstZeroRule = session.get('firstZeroRule', None)
        secondZeroRule = request.form['secondZeroRule']
        session['secondZeroRule'] = secondZeroRule
        secondHalf = True
        if secondZeroRule == '':
            flash('Please enter a response.', 'error')
            secondHalf = False
        
        return render_template('sftutorial3.html', firstZeroRule = firstZeroRule, secondZeroRule = secondZeroRule, page = 3, secondHalf = secondHalf)

    firstZeroRule = session.get('firstZeroRule', None)
    return render_template('sftutorial3.html',title="Sig Fig Tutorial", page = 3, firstZeroRule = firstZeroRule, secondHalf=False)

@sigfigs_blueprint.route('/sftutorial4', methods=['POST', 'GET'])
def sftutorial4():
    firstZeroRule = session.get('firstZeroRule', None)
    secondZeroRule = session.get('secondZeroRule', None)
    return render_template('sftutorial4.html',title="Sig Fig Tutorial", page = 4, firstZeroRule=firstZeroRule, secondZeroRule=secondZeroRule)

@sigfigs_blueprint.route('/sftutorial5', methods=['POST', 'GET'])
def sftutorial5():
    return render_template('sftutorial5.html',title="Sig Fig Tutorial", page = 5)

@sigfigs_blueprint.route('/roundingtutorial1', methods=['POST', 'GET'])
def roundingtutorial1():
    return render_template('roundingtutorial1.html',title="Rounding Tutorial", page = 1)

@sigfigs_blueprint.route('/roundingtutorial2', methods=['POST', 'GET'])
def roundingtutorial2():
    if request.method == 'POST':
        displayText = int(request.form['displayText'])
        displayText += 1
        roundedAnswer = request.form['5SigFigs']
        answers = []
        numCorrect = 0
        if displayText == 4 and roundedAnswer != '12.386':
            flash('Not quite correct.  Try again.', 'error')
            displayText = 3
        elif displayText>5:
            correctAnswers = ['0.00798','0.0080','0.008']
            for x in range(3):
                answers.append(request.form[str(3-x)+'SigFigs'])
                if CheckAnswer(correctAnswers[x],answers[x]):
                    flash('Correct!  :-)', 'correct')
                    numCorrect += 1
                else:
                    flash('Try again.', 'error')
    else:
        displayText=1
        roundedAnswer = ''
        answers = []
        numCorrect = 0

    return render_template('roundingtutorial2.html',title="Rounding Tutorial", page = 2, displayText=displayText, roundedAnswer = roundedAnswer, answers = answers, numCorrect = numCorrect)

@sigfigs_blueprint.route('/roundingtutorial3', methods=['POST', 'GET'])
def roundingtutorial3():
    if request.method == 'POST':
        displayText = int(request.form['displayText'])
        displayText += 1
        example3 = request.form['example3']
        answers = []
        numCorrect = 0
        if displayText == 2 and example3 != '2380':
            flash('Not quite correct.  Try again.', 'error')
            displayText = 1
        elif displayText > 3:
            correctAnswers = ['0.0998','0.10','0.1']
            for x in range(3):
                answers.append(request.form[str(3-x)+'SigFigs'])
                if CheckAnswer(correctAnswers[x],answers[x]):
                    flash('Correct!  :-)', 'correct')
                    numCorrect += 1
                else:
                    flash('Try again.', 'error')
    else:
        displayText=1
        example3 = ''
        answers = []
        numCorrect = 0

    return render_template('roundingtutorial3.html',title="Rounding Tutorial", page = 3, displayText=displayText, answers = answers, example3 = example3, numCorrect = numCorrect)

@sigfigs_blueprint.route('/roundingtutorial4', methods=['POST', 'GET'])
def roundingtutorial4():
    return render_template('roundingtutorial4.html',title="Rounding Tutorial", page = 4)

@sigfigs_blueprint.route('/scinottutorial1', methods=['POST', 'GET'])
def scinottutorial1():
    if request.method == 'POST':
        displayText = int(request.form['displayText'])
        displayText += 1
        if displayText == 2:
            decimal = request.form['decimal']
            power = request.form['exponent']
            decimals = ['1.5', '15', '150', '1500']
            powers = ['3','2','1','0']
            if decimal in decimals:
                index = decimals.index(decimal)
                if power != powers[index]:
                    flash('Incorrect power.  Try again.', 'error')
                    displayText = 1
            else:
                flash('Incorrect decimal value.  Try again.', 'error')       
                displayText = 1
        else:
            decimal = ''
            power = ''
    else:
        displayText=1
        decimal = ''
        power = ''

    return render_template('scinottutorial1.html',title="Scientific Notation Tutorial", page = 1, displayText = displayText, decimal = decimal, exponent=power)

@sigfigs_blueprint.route('/scinottutorial2', methods=['POST', 'GET'])
def scinottutorial2():
    if request.method == 'POST':
        decimals = []
        powers = []
        exponents = []
        values = []
        sciValues = []
        numCorrect = 0
        for item in range(4):
            decimals.append(request.form['decimal'+str(item)])
            exponents.append(request.form['exponent'+str(item)])
            values.append(request.form['value'+str(item)])
            powers.append(request.form['power'+str(item)])
            sciValues.append(request.form['sciValue'+str(item)])
            if CheckAnswer(powers[item], exponents[item]) and CheckAnswer(sciValues[item],decimals[item]):
                flash('Correct!  :-)', 'correct')
                numCorrect += 1
            elif CheckAnswer(powers[item], exponents[item]) and not CheckAnswer(sciValues[item],decimals[item]):
                flash('Correct power.  Wrong decimal value.', 'error')
            elif CheckAnswer(sciValues[item],decimals[item]) and not CheckAnswer(powers[item], exponents[item]):
                flash('Correct decimal value.  Wrong power.', 'error')
            else:
                flash('Both entries are incorrect.  Try again.', 'error')

    else:
        values = []
        sciValues = []
        powers = []
        decimals = []
        exponents = []
        numCorrect = 0
        for item in range(4):
            sigFigs = random.randrange(1,5)
            if item <= 1:
                power = random.randrange(0,7)
            else:
                power = random.randrange(-5,0)
            value = MakeNumber(sigFigs,power)
            values.append(value)
            powers.append(power)
            sciValues.append(ApplySciNotation(value, sigFigs))
        
    return render_template('scinottutorial2.html',title="Scientific Notation Tutorial", page = 2, values = values, decimals = decimals, exponents = exponents, sciValues = sciValues, powers = powers, numCorrect = numCorrect)

@sigfigs_blueprint.route('/scinottutorial3', methods=['POST', 'GET'])
def scinottutorial3():
    if request.method == 'POST':
        values = []
        sciValues = []
        powers = []
        answers = []
        numCorrect = 0
        for item in range(4):
            answers.append(request.form['answer'+str(item)])
            values.append(request.form['value'+str(item)])
            powers.append(request.form['power'+str(item)])
            sciValues.append(request.form['sciValue'+str(item)])
            if ',' in answers[item]:
                flash('Please remove the comma(s) from your answer.', 'error')
            elif CheckAnswer(values[item], answers[item]):
                flash('Correct!  :-)', 'correct')
                numCorrect += 1
            else:
                flash('Oops! Try again.', 'error')
    else:
        values = []
        sciValues = []
        powers = []
        answers = []
        numCorrect = 0
        for item in range(4):
            sigFigs = random.randrange(1,5)
            if item <= 1:
                power = random.randrange(0,7)
            else:
                power = random.randrange(-5,0)
            powers.append(power)
            values.append(MakeNumber(sigFigs,power))
            sciValues.append(ApplySciNotation(values[item], sigFigs))

    return render_template('scinottutorial3.html',title="Scientific Notation Tutorial", page = 3, values = values, answers = answers, sciValues = sciValues, powers = powers, numCorrect = numCorrect)

@sigfigs_blueprint.route('/scinottutorial4', methods=['POST', 'GET'])
def scinottutorial4():
    return render_template('scinottutorial4.html',title="Scientific Notation Tutorial", page = 4)

@sigfigs_blueprint.route('/sfcalcstutorial1', methods=['POST', 'GET'])
def sfcalcstutorial1():
    if request.method == 'POST':
        imageText = ['Assume two students measure the length of a small tile.  Their results are not the same, but the difference is small in this case.',
        'To predict the length of two tiles, the students simply double their measurements.  Note that the difference (uncertainty) in their results is LARGER than before.',
        'For five tiles, something interesting happens with the error in the predicted lengths.',
        'The difference between the results becomes too large to keep 2 decimal places, so the guess digit moves into the tenths place.',
        'What if each student calculated the area of the tile?','Multiplying measurements also increases error.','Since two digits are now uncertain, we must round each answer to maintain a single guess digit.']
        displayText = int(request.form['displayText']) + 1
        imageName = 'SFCalcs'+str(displayText-1)+'.png'
        return render_template('sfcalcstutorial1.html',title="Calculations with Sig Figs Tutorial", page = 1, displayText = displayText, imageText = imageText, imageName = imageName)

    displayText = 1
    return render_template('sfcalcstutorial1.html',title="Calculations with Sig Figs Tutorial", page = 1, displayText = displayText)

@sigfigs_blueprint.route('/sfcalcstutorial2', methods=['POST', 'GET'])
def sfcalcstutorial2():
    if request.method == 'POST':
        answers = []
        results = []
        values = []
        numCorrect = 0
        for item in range(4):
            values.append(request.form['value'+str(item)])
            if item < 2:
                answers.append(request.form['answer'+str(item)])
                results.append(request.form['result'+str(item)])
                if CheckAnswer(results[item], answers[item]):
                    flash('Correct!  :-)', 'correct')
                    numCorrect += 1
                else:
                    flash('Try again, or click to see the answer.', 'error')

        return render_template('sfcalcstutorial2.html',title="Calculations with Sig Figs Tutorial", page = 2, values = values, answers = answers, results = results, numCorrect = numCorrect)

    else:
        numCorrect = 0
        answers = []
        sigFigs = []
        powers = []
        values = []
        results = []
        for index in range(4):
            sigFigs.append(random.randrange(1,7))
            powers.append(random.randrange(-2,3))
            values.append(MakeNumber(sigFigs[index],powers[index]))
            flip = False
            if index == 1:
                results.append(multiplyValues(values[index-1],sigFigs[index-1],values[index],sigFigs[index]))
            elif index == 3 and float(values[index-1])/float(values[index])<1e-4:
                temp = values[index-1]
                values[index-1]=values[index]
                values[index]=temp
                results.append(divideValues(values[index-1],sigFigs[index-1],values[index],sigFigs[index]))
            elif index == 3:
                results.append(divideValues(values[index-1],sigFigs[index-1],values[index],sigFigs[index]))
            
    return render_template('sfcalcstutorial2.html',title="Calculations with Sig Figs Tutorial", page = 2, values = values, sigFigs = sigFigs, powers = powers, answers = answers, flip = flip, results = results, numCorrect = numCorrect)

@sigfigs_blueprint.route('/sfcalcstutorial3', methods=['POST', 'GET'])
def sfcalcstutorial3():
    if request.method == 'POST':
        answers = []
        results = []
        values = []
        numCorrect = 0
        for item in range(4):
            values.append(request.form['value'+str(item)])
            if item < 2:
                answers.append(request.form['answer'+str(item)])
                results.append(request.form['result'+str(item)])
                if CheckAnswer(results[item], answers[item]):
                    flash('Correct!  :-)', 'correct')
                    numCorrect += 1
                else:
                    flash('Try again, or click to see the answer.', 'error')

        return render_template('sfcalcstutorial3.html',title="Calculations with Sig Figs Tutorial", page = 3, values = values, answers = answers, results = results, numCorrect = numCorrect)
    else:
        numCorrect = 0
        answers = []
        sigFigs = []
        powers = []
        values = []
        results = []
        for index in range(4):
            iffyValue = True
            while iffyValue:
                sigFig = random.randrange(1,7)
                power = random.randrange(-3,2)
                value = MakeNumber(sigFig,power)
                iffyValue = CheckRounding(value,sigFig)
            sigFigs.append(sigFig)
            powers.append(power)
            values.append(value)
        if (float(values[0])>=10 and values[0].find('.') == -1 and sigFigs[0] < len(values[0])) or (float(values[1])>=10 and values[1].find('.') == -1 and sigFigs[1] < len(values[1])):
            results.append(addWithPlaceholders(values[0],values[1]))
        else:
            results.append(addValues(values[0],values[1]))
        if float(values[2]) < float(values[3]):
            values[2],values[3] = values[3],values[2]
            sigFigs[2],sigFigs[3] = sigFigs[3],sigFigs[2]
        if (float(values[2])>=10 and values[2].find('.') == -1 and sigFigs[2] < len(values[2])) or (float(values[3])>=10 and values[3].find('.') == -1 and sigFigs[3] < len(values[3])):
            results.append(subtractWithPlaceholders(values[2],values[3]))
        else:
            results.append(subtractValues(values[2],values[3]))
    return render_template('sfcalcstutorial3.html',title="Calculations with Sig Figs Tutorial", page = 3, values = values, sigFigs = sigFigs, powers = powers, answers = answers, results = results, numCorrect = numCorrect)

@sigfigs_blueprint.route('/sfcalcstutorial4', methods=['POST', 'GET'])
def sfcalcstutorial4():
    if request.method == 'POST':
        displayText = int(request.form['displayText'])
        response = int(request.form['response'])
        example = int(request.form['example'])
        if displayText == 0 and response < 2:
            answer = request.form['answer']
            if example == 0 and answer=='3':
                response += 1
            else:
                flash('This is NOT a trick question.  Count again...', 'error')
        elif displayText <= 2 and response < 1:
            response += 1
            example += 1
        else:
            response = 0
            example += 1
            displayText += 1
    else:
        displayText = 0
        example = 0
        response = 0

    return render_template('sfcalcstutorial4.html',title="Calculations with Sig Figs Tutorial", page = 4, displayText = displayText, example = example, response = response)