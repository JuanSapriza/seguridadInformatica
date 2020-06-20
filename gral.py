
import os
import signal

encoding = 'utf-8'
timeout_state = False

def timeout_handler(signum, frame):
    print ("\nTiempo de sesion finalizado. Presione Enter para continuar")
    global timeout_state
    timeout_state = True
    return

def input_timeout(timeout : int) -> str:
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    global timeout_state
    timeout_state = False
    ans = input("Tiempo máximo de respuesta {} segundos." .format(timeout))
    if timeout_state == True:
        ans = ""
        signal.alarm(0)
    return ans


def cls():
    None
    #os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input(">>> Presione una tecla para continuar...")

def debug( string: str):
    print(string)
