# -*-coding: utf-8 -*

import configparser
import datetime


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

    def _checkAnniversary(self, date):
        print('check anniversary')
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
