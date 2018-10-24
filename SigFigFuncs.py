import random
from flask import Flask, Blueprint
import cgi

operators = ['+','-','*','/']

class Number():
    def __init__(self, sigFigs, power):
        self.sigFigs = sigFigs
        self.power = power
        self.value = MakeNumber(sigFigs, power)

def MakeNumber(sigFigs, power):
    allDigits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    firstDigit = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    if power < 0:
        value = "0."+ -(power+1)*"0" + random.choice(firstDigit)
        for digit in range(sigFigs-1):
            value += random.choice(allDigits)
        return value
    elif sigFigs - power < 2:
        value = random.choice(firstDigit)
        for digit in range(sigFigs-1):
            if digit == sigFigs-2:
                value += random.choice(firstDigit)
            else:
                value += random.choice(allDigits)
        value += (power-sigFigs+1)*"0"
        return value
    else:
        value = random.choice(firstDigit)
        decimalLocation = power +1
        for digit in range(1, sigFigs+1):
            if digit == decimalLocation:
                value += "."
            else:
                value += random.choice(allDigits)
        return value

def RoundValue(value, sigFigs):        
    decimalIndex = value.find('.')
    if decimalIndex < 0:
        decimalIndex = len(value)

    if float(value)<1:
        placeholders = 0
        for x in range(2,len(value)):
            if value[x] == "0":
                placeholders += 1
            else:
                break

        roundToSigFigs = round(float(value)*10**placeholders,sigFigs)
        addPlaceholders = round(roundToSigFigs/10**placeholders,sigFigs+placeholders)

        if len(str(roundToSigFigs))-sigFigs < 3:
            result = str(addPlaceholders)+"0"*(2-(len(str(roundToSigFigs))-sigFigs))
        else:
            result = str(addPlaceholders)
        return result
    else:
        roundToSigFigs = round(float(value)/10**decimalIndex,sigFigs)
        addZeros = round(roundToSigFigs*10**decimalIndex,sigFigs-decimalIndex)

        if sigFigs <= decimalIndex:
            result = str(int(addZeros))
        elif len(str(addZeros))-sigFigs <= 0:
            result = str(addZeros)+"0"*(sigFigs-len(str(addZeros))+1)
        else:
            result = str(addZeros)

        return result

def CheckAnswer(result, answer):
    if answer == '':        #Check for null result.
        return False

    if answer[0] == ".":    #Convert '.xx' to '0.xx'.
        answer = "0"+answer

    if result == answer:    #Check for exact result.
        return True
    else:
        return False

def CheckRounding(result, sigFigs):
    if float(result)>=10 and sigFigs <= len(result):
        if result[sigFigs-1] == "0" and result.find('.') == -1:
            return True
        else:
            return False

def ApplySciNotation(result, sigFigs):
    if result[0] == "0":
        for x in range(2, len(result)):
            if result[x] != "0":
                startHere = x
                if sigFigs > 1:
                    sciNot = result[x]+"."
                else:
                    sciNot = result[x]
                break
        for digit in range(startHere+1,len(result)):
            sciNot += result[digit]
    elif result.find(".") >= 0:
        sciNot = result[0]+"."
        for x in range(1,sigFigs+1):
            if result[x] != ".":
                sciNot += result[x]
    else:
        sciNot = result[0]
        if sigFigs > 1:
            sciNot += "."        
        for x in range(1,sigFigs):
            sciNot += result[x]
    return sciNot

def findDecimalPlaces(value):
    decimalIndex = value.find(".")
    if decimalIndex>0:
        decimalPlaces = len(value)-decimalIndex-1
    else:
        decimalPlaces = 0
    return decimalPlaces

def addValues(first,second):
    firstDP = findDecimalPlaces(first)
    secondDP = findDecimalPlaces(second)
    if firstDP == 0 or secondDP == 0:
        result = str(int(round((float(first)+float(second)),0)))
        return result
    elif firstDP > secondDP:
        result = str(round(float(first)+float(second),secondDP))
        resultDP = findDecimalPlaces(result)
        if resultDP < secondDP:
            result += "0"
    else:
        result = str(round(float(first)+float(second),firstDP))
        resultDP = findDecimalPlaces(result)
        if resultDP < firstDP:
            result += "0"
    return result

def addWithPlaceholders(first,second):
    if float(first)>=1 and float(second)>=1:
        zeroCount = max(first.count("0"),second.count("0"))
    elif float(first)<1:
        zeroCount = second.count("0")
    else:
        zeroCount = first.count("0")
    temp1 = float(first)/10**zeroCount
    temp2 = float(second)/10**zeroCount
    result = str(int(round(temp1+temp2,0))*10**zeroCount)
    return result

def subtractValues(first,second):
    firstDP = findDecimalPlaces(first)
    secondDP = findDecimalPlaces(second)
    if firstDP == 0 or secondDP == 0:
        result = str(int(round((float(first)-float(second)),0)))
        return result
    elif firstDP > secondDP:
        result = str(round(float(first)-float(second),secondDP))
        resultDP = findDecimalPlaces(result)
        if resultDP < secondDP:
            result += "0"
    else:
        result = str(round(float(first)-float(second),firstDP))
        resultDP = findDecimalPlaces(result)
        if resultDP < firstDP:
            result += "0"*(firstDP-resultDP)
    return result

def subtractWithPlaceholders(first,second):
    if float(first)>=1 and float(second)>=1:
        zeroCount = max(first.count("0"),second.count("0"))
    elif float(first)<1:
        zeroCount = second.count("0")
    else:
        zeroCount = first.count("0")
    temp1 = float(first)/10**zeroCount
    temp2 = float(second)/10**zeroCount
    result = str(int(round(temp1-temp2,0))*10**zeroCount)
    return result

def multiplyValues(value1, sf1, value2, sf2):
    sigFigs = min(sf1, sf2)
    product = str(float(value1)*float(value2))
    result = RoundValue(product, sigFigs)

    return result

def divideValues(value1, sf1, value2, sf2):
    sigFigs = min(sf1, sf2)
    quotient = str(float(value1)/float(value2))
    result = RoundValue(quotient, sigFigs)

    return result