# -*-coding:Latin-1 -*

import configparser
import datetime

from pathlib import Path


class savedContext():
    # This class will parse the .ini config file

    def __init__(self):
        # Reading the previously saved context
        self.file = 'saved_context.ini'
        self.config = configparser.ConfigParser()
        self.config.read(self.file)

        # Counter
        counter = self.config['Misc']['Counter']
        self.config['Misc']['Counter'] = str(int(counter)+1)

        # Date
        # todayDate = datetime.datetime.today
        today = datetime.datetime.today
        print(today)

        with open(self.file, 'w') as contextFile:
            self.config.write(contextFile)

# def getOutputFilePath(self):
#     return self.outputFilePath

# def getVerbosityLevel(self):
#     return self.verbosityLevel
