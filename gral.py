
import os
import threading as t
from time import sleep

encoding = 'utf-8'
timeout_state = False

def timeout_handler():
    cls()
    print ("> Tiempo de sesion finalizado. Presione Enter para continuar")
    global timeout_state
    timeout_state = True
    return

def input_timeout(timeout : int) -> str:
    #signal.signal(signal.SIGALRM, timeout_handler)
    #signal.alarm(timeout)
    timer = t.Timer(timeout, timeout_handler)
    timer.start()
    global timeout_state
    timeout_state = False
    ans = input("Tiempo máximo de respuesta {} segundos." .format(timeout))
    timer.cancel()
    if timeout_state == True:
        ans = ""
    return ans


def cls():
    #None
    os.system('cls' if os.name == 'nt' else 'clear')

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
