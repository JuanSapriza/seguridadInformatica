
import os
from time import sleep

encoding = 'utf-8'

def cls():
    None
    #os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input(">>> Presione una tecla para continuar...")

def debug( string: str):
    print(string)

def waitms( ms: int):
    sleep(ms/1000)

def popUp( msg: str ):
    cls()
    print(msg)
    waitms(2000)
    cls()