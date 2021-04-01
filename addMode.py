# -*-coding: utf-8 -*

import sys
import os
import json
import re
import datetime
import shutil
import configparser
import ntpath

from pathlib import Path


class addMode():
    # This class is used to add capsules

    def __init__(self):
        # Date
        now = datetime.datetime.now()
        self.currentDate = datetime.date(
            year=now.year, month=now.month, day=now.day)

        # Reading the previously saved context
        self.savedContextFile = 'saved_context.ini'
        self.configParser = configparser.ConfigParser()
        self.configParser.read(self.savedContextFile)

        self.savedCapsulesNb = int(self.configParser['Capsules']['saved'])

    def run(self):
        # Input: file path
        fileToAddPath = input(
            '-Entrez le chemin du fichier à insérer dans la capsule. Il sera stocké dans les fichiers du programme :\n> ')
        fileToAddPath.strip(' ')

        fileToAddObj = Path(fileToAddPath)
        if not fileToAddObj.is_file():
            print('ERREUR : Le format de ' +
                  fileToAddPath + ' n\'est pas correct.\n')
            sys.exit(-1)
        # Gmail max size
        fileByteSize = os.stat(fileToAddPath).st_size
        if fileByteSize >= (25*1024*1024):
            print('ERREUR : Le fichier fait ' + str(round(((float(fileByteSize))/(1024.0*1024.0)), 1)) +
                  'Mo et dépasse donc la taille max de 25Mo imposée par Gmail.\n')
            sys.exit(-1)

        # Input: burying time
        buryingTimeRaw = input(
            '-Entrez le temps d\'enfouissement de la capsule :\nFormat: 20J pour 20 jours, 6M pour 6 mois, 2A pour 2 ans...\n> ')
        buryingTime = buryingTimeRaw.strip(' .-_,')
        buryingTimeValue = re.findall(r'^[0-9]+', buryingTime)
        buryingTimeUnit = re.findall(r'[JMA]$', buryingTime)

        if (len(buryingTimeValue) != 1) or (len(buryingTimeUnit) != 1):
            print('ERREUR : Le format de ' + buryingTimeRaw +
                  ' n\'est pas correct (20J pour 20 jours, 6M pour 6 mois, 2A pour 2 ans...).\n')
            sys.exit(-1)

        # Input: name
        ownerName = input(
            '-Entrez votre prénom :\n> ')
        ownerName = ownerName.strip(' .-_,')

        if len(ownerName) == 0:
            print('ERREUR : Le format du prénom n\'est pas correct.\n')
            sys.exit(-1)

        # Input: email
        receiverEmail = input(
            '-Entrez l\'adresse email à laquelle sera envoyée l\'alerte après le temps d\'enfouissement :\n> ')
        receiverEmail = receiverEmail.strip(' .-_,')

        if not re.search(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', receiverEmail):
            print('ERREUR : Le format de ' + receiverEmail +
                  ' n\'est pas correct.\n')
            sys.exit(-1)

        # Increment the nb of stored capsules
        self.savedCapsulesNb = self.savedCapsulesNb+1

        # Create folder(s) and store the file
        dirToStoreNewCapsule = 'capsules/'+str(self.savedCapsulesNb)
        os.mkdir(dirToStoreNewCapsule)
        newCapsuleFile = shutil.copyfile(
            fileToAddPath, dirToStoreNewCapsule+'/'+str(ntpath.basename(fileToAddPath)))

        # Set the new file as read only
        os.chmod(path=newCapsuleFile, mode=0o444)

        # Format the JSON
        jsonDescrDict = {
            'capsule': {
                'index': str(self.savedCapsulesNb),
                'owner_name': ownerName,
                'file': str(ntpath.basename(newCapsuleFile)),
                'email': receiverEmail,
                'creation_date': str(self.currentDate),
                'burying_time': {
                    'value': buryingTimeValue[0],
                    'unit': buryingTimeUnit[0]
                }
            }
        }

        # Dump it into info.json
        jsonDescrDump = json.dumps(jsonDescrDict, indent=4, ensure_ascii=False)
        with open(dirToStoreNewCapsule+'/info.json', 'w', encoding='utf-8') as jsonFile:
            jsonFile.write(jsonDescrDump)

    def saveContextAndEnd(self):
        self.configParser['Capsules']['saved'] = str(self.savedCapsulesNb)

        with open(self.savedContextFile, 'w') as contextFile:
            self.configParser.write(contextFile)
