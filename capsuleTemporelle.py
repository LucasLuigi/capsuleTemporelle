# -*-coding:Latin-1 -*

import sys
import time

from savedContext import savedContext


if __name__ == '__main__':
    print('Bonjour\n')

    # Reading saved context file from previous execution
    savedContextInst = savedContext()
    time.sleep(3)
