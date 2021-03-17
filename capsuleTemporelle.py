# -*-coding:Latin-1 -*

import sys
import argparse
import time

from pathlib import Path
from shutil import copyfile

from dailyMode import dailyMode


def firstExecution():
    copyfile('templates\saved_context.template', 'saved_context.ini')


if __name__ == '__main__':
    print('- capsuleTemporelle- \n')

    # Argument Parser         #
    ###########################
    parser = argparse.ArgumentParser(
        description='Gestionnaire de capsules temporelles')
    parser.add_argument('-d', action='store_true', dest='flagDaily',
                        help='Daily use - Usage journalier pour verifier l\'anniversaire des capsules existantes')
    parser.add_argument('--add', action='store', nargs='?', dest='fileToAdd',
                        help='Add - Ajoute un fichier a la capsule temporelle. Doit etre suivi du chemin du fichier')
    args = parser.parse_args()

    # First execution         #
    ###########################
    iniFile = Path('./saved_context.ini')
    if not iniFile.is_file():
        # Create .ini file in case of first execution
        firstExecution()

    # Daily mode              #
    ###########################
    if(args.flagDaily == True):
        # Reading saved context file from previous execution
        dailyMode = dailyMode()

        # Run missed daily modes, including today's one
        dailyMode.run()

        # Save changed values offline to end the daily mode execution
        # COMMENTED FOR TEST PURPOSE ONLY
        # dailyMode.saveAndEnd()
    else:
        # Add mode                #
        ###########################
        if args.fileToAdd != None:
            # Add mode
            print('Ajout de '+args.fileToAdd +
                  ' a la liste des capsules temporelles.\n')
    time.sleep(3)
