# -*-coding: utf-8 -*

import sys
import os
import argparse

from pathlib import Path
from shutil import copyfile

from dailyMode import dailyMode
from addMode import addMode


def firstExecution():
    os.remove('saved_context.ini')
    # Init the offline context file
    copyfile('templates/saved_context.template', 'saved_context.ini')
    # Create the storage and archive folders. No error will be raised if the folder already exists
    os.makedirs('capsules', exist_ok=True)


if __name__ == '__main__':
    print('- capsuleTemporelle - \n')

    # Argument Parser         #
    ###########################
    parser = argparse.ArgumentParser(
        description='Gestionnaire de capsules temporelles')
    parser.add_argument('-d', action='store_true', dest='flagDaily',
                        help='Daily mode - Usage journalier pour vérifier l\'anniversaire des capsules existantes')
    parser.add_argument('-r', action='store_true', dest='flagRecapMail',
                        help='Recap mode - Provoque l\'envoi du mail de récap, disponible seulement avec l\'option -d')
    # parser.add_argument('--add', action='store', nargs='?', dest='fileToAdd',
    #                     help='Add - Ajoute un fichier a la capsule temporelle. Doit etre suivi du chemin du fichier')
    parser.add_argument('-a', action='store_true', dest='flagAdd',
                        help='Add mode - Ajoute une capsule temporelle. Les infos du fichier seront demandées en suivant')
    args = parser.parse_args()

    # First execution         #
    ###########################
    iniFile = Path('./saved_context.ini')
    capsulesFolder = Path('./capsules')
    if not iniFile.is_file() or not capsulesFolder.is_dir():
        # Create .ini file in case of first execution
        firstExecution()

    # Archive folder: must be created if it has not been done before. Not just at first execution
    archivesFolder = Path('./archives')
    if not archivesFolder.is_dir():
        os.makedirs('archives', exist_ok=True)

    # Daily mode              #
    ###########################
    if args.flagDaily == True:
        # Daily mode init: Reading saved context file from previous execution
        dailyMode = dailyMode(args.flagRecapMail)

        # Run missed daily modes, including today's one
        dailyMode.run()

        # Save changed values offline to end the daily mode execution
        # COMMENTED FOR TEST PURPOSE ONLY
        dailyMode.saveContextAndEnd()
    else:
        # Add mode                #
        ###########################
        if args.flagAdd == True:
            print('Ajout d\'une capsule.')

            # Add mode init: Reading saved context file from previous execution
            addMode = addMode()

            # Run the add process
            addMode.run()

            # Save changed values offline to end the daily mode execution
            addMode.saveContextAndEnd()
