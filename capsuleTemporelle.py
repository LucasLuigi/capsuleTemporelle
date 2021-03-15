# -*-coding:Latin-1 -*

import sys
import argparse
import time

from dailyMode import dailyMode


if __name__ == '__main__':
    print('- capsuleTemporelle- \n\n')

    parser = argparse.ArgumentParser(
        description='Gestionnaire de capsules temporelles')
    parser.add_argument('-d', action='store_true', dest='flagDaily',
                        help='Daily use - Usage journalier pour verifier l\'anniversaire des capsules existantes')
    parser.add_argument('--add', action='store', nargs='?', dest='fileToAdd',
                        help='Add - Ajoute un fichier a la capsule temporelle. Doit etre suivi du chemin du fichier')
    args = parser.parse_args()

    if(args.flagDaily == True):
        # Daily execution
        # Reading saved context file from previous execution
        dailyModeInst = dailyMode()
    else:
        if args.fileToAdd != None:
            # Add mode
            print('Ajout de '+args.fileToAdd +
                  ' a la liste des capsules temporelles.\n')

    time.sleep(3)
