# THIS DOES NOT WORK AT ALL
# This is just a very old implementation that I worked on several versions ago when I still used Python 3.6 instead of 2.7

import fileinput
import re

regexOrdering = '"(\\d+)": (\\d+),?'
patternOrdering = re.compile(regexOrdering)

regexChoice = '<p.+>(.+)</p>'
patternChoice = re.compile(regexChoice)

regexValue1 = '"(\\d+)": \\['
patternValue1 = re.compile(regexValue1)

regexValue2 = '"(\\d+)",?'
patternValue2 = re.compile(regexValue2)

regexInput = '"input": "(.+)",?'
patternInput = re.compile(regexInput)

regexWord = '"word": "(.+)",?'
patternWord = re.compile(regexWord)

regexWid = '"wid": "(\\d+)",?'
patternWid = re.compile(regexWid)

regexFreeResponse = '"value": "(.+)",?'
patternFreeResponse = re.compile(regexFreeResponse)

labels = list()
correct = list()
values = list()
inputs = list()
words = list()
wids = list()

questionCount = 0
lineCount = 0

alphabet = {
    '0': 'A',
    '1': 'B',
    '2': 'C',
    '3': 'D',
    '4': 'E',
    '5': 'F',
    '6': 'G',
    '7': 'H',
    '8': 'I',
    '9': 'J',
    '10': 'K',
    '11': 'L',
    '12': 'M',
    '13': 'N',
    '14': 'O',
    '15': 'P',
    '16': 'Q',
    '17': 'R',
    '18': 'S',
    '19': 'T',
    '20': 'U',
    '21': 'V',
    '22': 'W',
    '23': 'X',
    '24': 'Y',
    '25': 'Z',
}

infile = fileinput.input('assessment_index.json')
for line in infile:
    if '"Class": "Poll",' in line:
        while '"Class": "Question",' not in line:
            line = next(infile)
            lineCount += 1
    if '"Class": "FillInTheBlankWithWordBankPart",' in line:
        while '"wordbank": null' not in line:
            line = next(infile)
            if '"input": <div' in line:
                print('yes')
                print(lineCount)
                line = next(infile)
                break
            if '"input": ' in line:
                matcher = patternInput.search(line)
                if matcher is not None:
                    match = str(matcher.group(1))
                    occurrences = len([re.finditer('<div.+>', match)])
                    new = re.compile('(.+)<input.+>(.+)(<input.+>(.+)){' + str(occurrences - 1) + ',}').search(match)
                    inputed = re.sub('<input.+>', '$$SPLIT$$', str(new.group(0)))
                    print(line)
                    print(inputed)
                    inputs = inputed.split('$$SPLIT$$')
                    print(inputs)
            if '"value": {' in line:
                while '},' not in line:
                    line = next(infile)
                    matcher1 = patternValue1.search(line)
                    if matcher1 is not None:
                        line = next(infile)
                        matcher2 = patternValue2.search(line)
                        if matcher2 is not None:
                            answer = matcher2.group(1)
                            correct.append(answer)
                            print(correct)
                        lineCount += 1
                    lineCount += 1
            if '"wordbank": {' in line:
                while '"unique": ' not in line:
                    line = next(infile)
                    if '"wid": ' in line:
                        matcher1 = patternWid.search(line)
                        if matcher1 is not None:
                            line = next(infile)
                            if '"word": ' in line:
                                matcher2 = patternWord.search(line)
                                if matcher2 is not None:
                                    wid = matcher1.group(1)
                                    word = matcher2.group(1)
                                    wids.append(wid)
                                    words.append(word)
                            lineCount += 1
                    lineCount += 1
            lineCount += 1
        responseCount = 1
        inputCount = len(inputs)
        print(len(inputs))
        print(inputs)
        output = open('output' + str(questionCount) + '.txt', 'w+')
        if inputCount is 2:
            while responseCount < inputCount:
                output.write('<responseDeclaration identifier="RESPONSE' + str(responseCount) +
                             '" cardinality="single" baseType="identifier">\n')
                output.write('\t<correctResponse>\n')
                output.write('\t\t<value>' + correct.pop(0) + '</value>\n')
                output.write('\t</correctResponse>\n')
                output.write('</responseDeclaration>\n\n')
                responseCount += 1
            responseCount = 1
            output.write(inputs.pop(0))
            while responseCount < inputCount:
                output.write('\n<inlineChoiceInteraction responseIdentifier="RESPONSE'
                             + str(responseCount) + '" shuffle="false">')
                while len(wids) is not 0 and len(words) is not 0:
                    output.write('\n\t<inlineChoice identifier="' + wids.pop(0) +
                                 '">' + words.pop(0) + '</inlineChoice>')
                output.write('\n</inlineChoiceInteraction>\n')
                output.write(inputs.pop(0))
                responseCount += 1
        if inputCount is 3:
            output.write('<responseDeclaration identifier="RESPONSE1" cardinality="single" baseType="identifier">\n')
            output.write('\t<correctResponse>\n')
            output.write('\t\t<value>' + correct.pop(0) + '</value>\n')
            output.write('\t</correctResponse>\n')
            output.write('</responseDeclaration>\n')
            output.write('<responseDeclaration identifier="RESPONSE2" cardinality="single" baseType="identifier">\n')
            output.write('\t<correctResponse>\n')
            output.write('\t\t<value>' + correct.pop(0) + '</value>\n')
            output.write('\t</correctResponse>\n')
            output.write('</responseDeclaration>\n\n')
            output.write(inputs.pop(0))
            output.write('\n\t<inlineChoiceInteraction responseIdentifier="RESPONSE1" shuffle="false">')
            widt = wids.copy()
            wordt = words.copy()
            while len(widt) is not 0 and len(wordt) is not 0:
                output.write('\n\t\t<inlineChoice identifier="' + widt.pop(0) + '">' + wordt.pop(0) + '</inlineChoice>')
            output.write('\n</inlineChoiceInteraction>\n')
            output.write(inputs.pop(0))
            output.write('\n\t<inlineChoiceInteraction responseIdentifier="RESPONSE2" shuffle="false">')
            while len(widt) is not 0 and len(wordt) is not 0:
                output.write('\n\t\t<inlineChoice identifier="' + widt.pop(0) + '">' + wordt.pop(0) + '</inlineChoice>')
            output.write('\n</inlineChoiceInteraction>\n')
            output.write(inputs.pop(0))
        output.close()
        questionCount += 1
    lineCount += 1
