# -*-coding:Latin-1 -*

import configparser
import datetime

# from pathlib import Path


class dailyMode():
    # This class will parse the .ini config file

    def __init__(self):
        # TODO Check if .ini file exists and if not create one

        # Reading the previously saved context
        self.savedContextFile = 'saved_context.ini'
        self.configParser = configparser.ConfigParser()
        self.configParser.read(self.savedContextFile)

        # Counter
        counter = self.configParser['Misc']['Counter']
        self.configParser['Misc']['Counter'] = str(int(counter)+1)

        # Date
        self.latestDate = datetime.date.fromisoformat(
            self.configParser['Last execution']['Date'])

        now = datetime.datetime.now()

        # Current execution date is rebuilt without its hour:mn:s:ms attributes
        self.currentDate = datetime.date(
            year=now.year, month=now.month, day=now.day)
        self.configParser['Last execution']['Date'] = str(self.currentDate)

        oneDayDelta = datetime.timedelta(days=1.0)

        if(self.currentDate - self.latestDate < oneDayDelta):
            print('<1')
            # TODO
        elif(self.currentDate - self.latestDate == oneDayDelta):
            print('==1')
            # TODO
        else:
            print('>1')
            # TODO

        with open(self.savedContextFile, 'w') as contextFile:
            self.configParser.write(contextFile)
