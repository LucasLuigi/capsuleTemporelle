# -*-coding: utf-8 -*

import sys
import os
import time
import configparser
import datetime
import json
import yagmail

from pathlib import Path

MONTHS_ARRAY = ['MONTH0', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai',
                'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']


class dailyMode():
    # This class will parse the .ini config file

    def __init__(self, triggerRecapMail):
        # Argument: boolean
        self.triggerRecapMail = triggerRecapMail

        # Reading the previously saved context
        self.savedContextFile = 'saved_context.ini'
        self.configParser = configparser.ConfigParser()
        self.configParser.read(self.savedContextFile)

        # Counter
        counter = self.configParser['Misc']['counter']
        self.configParser['Misc']['counter'] = str(int(counter)+1)

        # Date
        now = datetime.datetime.now()

        # Capsules
        try:
            self.savedCapsulesNb = int(self.configParser['Capsules']['saved'])
        except ValueError:
            # Should not happen as the init value is 0
            print('ERREUR : Il y a un problème avec le fichier .ini, Capsules > Saved n\'est pas défini ou n\'est pas un nombre\n')
            sys.exit(-2)

        try:
            self.latestDate = datetime.date.fromisoformat(
                self.configParser['Last execution']['date'])
        except ValueError:
            # During the first execution, the latest execution date will be empty
            # To avoid fatal error, it is set to the day before today (to ensure at least one execution)
            oneDayDelta = datetime.timedelta(days=1.0)
            self.latestDate = datetime.date(
                year=now.year, month=now.month, day=now.day) - oneDayDelta

        # Current execution date is rebuilt without its hour:mn:s:ms attributes
        self.currentDate = datetime.date(
            year=now.year, month=now.month, day=now.day)

        # Parse the email used to send the reminders, store in another file for privacy reasons
        with open('config_me_with_your_gmail_address.txt', 'r', encoding='utf-8') as configGmailFile:
            self.GMAIL_SENDER_EMAIL = configGmailFile.read()
            self.GMAIL_SENDER_EMAIL.strip(' .')
        if self.GMAIL_SENDER_EMAIL == None:
            print(
                'ERREUR : Le fichier config_me_with_your_gmail_address est censé contenir votre adresse gmail et ce n\'est pas le cas\n')
            # TODO Log in on log file?
            sys.exit(-4)

    def _sendRecapMail(self, hasBeenManuallyTriggered):
        if hasBeenManuallyTriggered:
            print('INFO : Envoi de l\'email de récap provoqué par l\'option -r\n')
        else:
            print('INFO : Envoi de l\'email mensuel de récap\n')

        identation = '                '

        # Extracting the useful infos
        currentMonth = MONTHS_ARRAY[self.currentDate.month]
        wd = os.getcwd()
        capsulesFolderPath = wd + '\\capsules'

        currentNbOfSavedCaps = 0
        listOfCaps = ''
        for capsuleFolder in os.scandir(capsulesFolderPath):
            if capsuleFolder.is_dir():
                currentNbOfSavedCaps += 1
                jsonDescrPath = capsuleFolder.path + '\\info.json'
                with open(jsonDescrPath, 'r', encoding='utf-8') as jsonDescrFile:
                    jsonDescrFileContent = jsonDescrFile.read()
                    jsonDescrDict = json.loads(jsonDescrFileContent)

                listOfCaps = listOfCaps + identation+'<li>'
                listOfCaps = listOfCaps + jsonDescrDict['capsule']['file']+' ajouté le '+jsonDescrDict['capsule']['creation_date'] + \
                    ' par '+jsonDescrDict['capsule']['owner_name']+' pendant ' + \
                    jsonDescrDict['capsule']['burying_time']['value']

                if jsonDescrDict['capsule']['burying_time']['unit'] == 'A':
                    listOfCaps = listOfCaps+' an'
                elif jsonDescrDict['capsule']['burying_time']['unit'] == 'M':
                    listOfCaps = listOfCaps+' mois'
                elif jsonDescrDict['capsule']['burying_time']['unit'] == 'J':
                    listOfCaps = listOfCaps+' jour'

                if (int(jsonDescrDict['capsule']['burying_time']['value']) > 1) and jsonDescrDict['capsule']['burying_time']['unit'] != 'M':
                    listOfCaps = listOfCaps+'s'

                listOfCaps = listOfCaps + '.</li>\n'

        # Building the mail body from the template and above informations
        with open('templates/mail_template_recap.html', 'r', encoding='utf-8') as templateBody:
            templateBodyContent = templateBody.read()

        body = templateBodyContent.replace(
            'MONTH', currentMonth)
        body = body.replace(
            'LAST_EXEC_DATE', self.configParser['Last execution']['date'])
        body = body.replace('TOTAL_SAVED_CAPS',
                            self.configParser['Capsules']['saved'])
        body = body.replace('CURRENT_SAVED_CAPS', str(currentNbOfSavedCaps))
        body = body.replace('LIST_OF_CAPS', listOfCaps)

        # Logging and sending the email with Yagmail
        yag = yagmail.SMTP(
            {self.GMAIL_SENDER_EMAIL: 'Capsule Temporelle'})
        yag.send(
            to=self.GMAIL_SENDER_EMAIL,
            subject='capsuleTemporelle - Récapitulatif du mois de '+currentMonth,
            contents=body
        )

    def _sendAnniversaryEmail(self, executionDate, jsonDescrDict):
        print('INFO : Envoi de l\'email d\'anniversaire\n')

        # Extracting the useful infos from the json
        receiver = jsonDescrDict['capsule']['email']

        buryingPeriodComplete = jsonDescrDict['capsule']['burying_time']['value']

        if jsonDescrDict['capsule']['burying_time']['unit'] == 'A':
            buryingPeriodComplete = buryingPeriodComplete+' an'
        elif jsonDescrDict['capsule']['burying_time']['unit'] == 'M':
            buryingPeriodComplete = buryingPeriodComplete+' mois'
        elif jsonDescrDict['capsule']['burying_time']['unit'] == 'J':
            buryingPeriodComplete = buryingPeriodComplete+' jour'

        if (int(jsonDescrDict['capsule']['burying_time']['value']) > 1) and jsonDescrDict['capsule']['burying_time']['unit'] != 'M':
            buryingPeriodComplete = buryingPeriodComplete+'s'

        buryingDate = datetime.date.fromisoformat(
            jsonDescrDict['capsule']['creation_date'])

        burrying_day = str(buryingDate.day)
        if len(burrying_day) == 1:
            burrying_day = '0'+burrying_day

        burrying_month = str(buryingDate.month)
        if len(burrying_month) == 1:
            burrying_month = '0'+burrying_month

        burrying_year = str(buryingDate.year)

        buryingDateForTheMail = burrying_day + \
            '/' + burrying_month + '/' + burrying_year

        name = jsonDescrDict['capsule']['owner_name']

        # Building the mail body from the template and above informations
        with open('templates/mail_template.html', 'r', encoding='utf-8') as templateBody:
            templateBodyContent = templateBody.read()

        body = templateBodyContent.replace(
            'SUBST_BURYING_PERIOD_COMPLETE', buryingPeriodComplete)
        body = body.replace(
            'SUBST_NAME', name)
        body = body.replace('SUBST_BURYING_DATE', buryingDateForTheMail)

        filename = 'capsules/' + \
            jsonDescrDict['capsule']['index'] + \
            '/'+jsonDescrDict['capsule']['file']

        # Logging and sending the email with Yagmail
        yag = yagmail.SMTP(
            {self.GMAIL_SENDER_EMAIL: 'Capsule Temporelle'})
        yag.send(
            to=receiver,
            subject='Une capsule temporelle a emmergé',
            contents=body,
            attachments=filename,
            bcc=self.GMAIL_SENDER_EMAIL
        )

    def _checkAnniversary(self, executionDate):
        for i in range(self.savedCapsulesNb):
            # i start from 0 and goes to savedCapsulesNb-1, but the actual existing capsules are in directories going from 1 to savedCapsulesNb
            indexCapsule = i+1
            capsulesFolderPathObj = Path('./capsules/'+str(indexCapsule))
            if capsulesFolderPathObj.is_dir():
                jsonDescrPath = './capsules/'+str(indexCapsule)+'/info.json'
                with open(jsonDescrPath, 'r', encoding='utf-8') as jsonDescrFile:
                    jsonDescrFileContent = jsonDescrFile.read()
                    jsonDescrDict = json.loads(jsonDescrFileContent)
                capsuleCreationDate = datetime.date.fromisoformat(
                    jsonDescrDict['capsule']['creation_date'])
                capsuleBuryingTimeValue = int(
                    jsonDescrDict['capsule']['burying_time']['value'])
                capsuleBuryingTimeUnit = jsonDescrDict['capsule']['burying_time']['unit']
                if capsuleBuryingTimeUnit == 'A':
                    deltaDays = 365 * capsuleBuryingTimeValue
                elif capsuleBuryingTimeUnit == 'M':
                    deltaDays = 30 * capsuleBuryingTimeValue
                elif capsuleBuryingTimeUnit == 'J':
                    deltaDays = capsuleBuryingTimeValue
                else:
                    # Should not happen, the file is bad written
                    print(
                        'ERREUR : Il y a un problème avec info.json, unit est '+capsuleBuryingTimeUnit+'et pas A, M ou J\n')
                    # TODO log this in a file and maybe clean the broken capsule instead of exiting?
                    sys.exit(-3)
                capsuleTimeDelta = datetime.timedelta(
                    days=deltaDays)
                if capsuleCreationDate + capsuleTimeDelta == executionDate:
                    print('INFO : Date d\'enfouissement atteinte ('+str(jsonDescrDict['capsule']['burying_time']['value'])
                          + jsonDescrDict['capsule']['burying_time']['unit']+') pour '
                          + jsonDescrDict['capsule']['file'])
                    self._sendAnniversaryEmail(executionDate, jsonDescrDict)

                    # Archive the capsule
                    wd = os.getcwd()
                    os.replace(wd+'\\capsules\\'+str(indexCapsule)+'\\',
                               wd+'\\archives\\'+str(indexCapsule)+'\\')

    def run(self):
        if self.triggerRecapMail:
            self._sendRecapMail(True)

        oneDayDelta = datetime.timedelta(days=1.0)
        if(self.currentDate - self.latestDate < oneDayDelta):
            print('INFO : Le mode journalier a déjà été exécuté aujourd\'hui.')
            # Nothing to do, the daily actions have already been executed today
        elif(self.currentDate - self.latestDate >= oneDayDelta):
            # date object to iterate between the latest execution date+1 and today to execute the missed daily actions
            iterDate = self.latestDate + oneDayDelta

            while self.currentDate >= iterDate:
                # Recap mail
                if iterDate.day == 1:
                    self._sendRecapMail(False)

                self._checkAnniversary(iterDate)

                iterDate = iterDate + oneDayDelta

    def saveContextAndEnd(self):
        self.configParser['Last execution']['date'] = str(self.currentDate)

        with open(self.savedContextFile, 'w') as contextFile:
            self.configParser.write(contextFile)
