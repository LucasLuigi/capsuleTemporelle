# -*-coding: utf-8 -*

import sys
import configparser
import datetime
import json

from pathlib import Path


class dailyMode():
    # This class will parse the .ini config file

    def __init__(self):
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
                    # TODO

    def run(self):
        oneDayDelta = datetime.timedelta(days=1.0)
        if(self.currentDate - self.latestDate < oneDayDelta):
            print('<1')
            # Nothing to do, the daily actions have already been executed today
        elif(self.currentDate - self.latestDate >= oneDayDelta):
            print('>=1')

            # date object to iterate between the latest execution date+1 and today to execute the missed daily actions
            iterDate = self.latestDate + oneDayDelta

            while self.currentDate >= iterDate:
                print(str(iterDate))
                self._checkAnniversary(iterDate)

                iterDate = iterDate + oneDayDelta

    def saveContextAndEnd(self):
        self.configParser['Last execution']['date'] = str(self.currentDate)

        with open(self.savedContextFile, 'w') as contextFile:
            self.configParser.write(contextFile)
