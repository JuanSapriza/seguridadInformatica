import gral as g
from gral import encoding
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import encryptionFwk as c
import userInfo as u
from userInfo import addUser
import os

def showMenu( user: u.User ) -> bool:
    #g.cls()
    print( "#### MENU PRINCIPAL ####" )
    print("Usuario: " + str(user.index) +" > " + user.userName + " | " + str(user.role) )
    print("   ¿Qué desea hacer? ")
    print(" 1. Encriptar Archivo")
    print(" 2. Desencriptar Archivo")
    print(" 3. Agregar Nuevo Usuario")
    action = input()
    if action == "":
        return True
    function2Perfom(int(action))(user)
    return False

def function2Perfom( index: int ):
    switch = {
        1 :encryptFile,
        2 :decryptFile,
        3 :newUser,
    }
    return switch.get(index,False)
# TODO: que se puede encriptar un .txt
def encryptFile( user: u.User ):
    g.cls()
    print(" #### ENCRIPTAR ARCHIVO ####")
    root = Tk()
    root.wm_withdraw()
    fileName = askopenfilename(title="Elegir Archivo", filetypes=([("Binarios", "*.bin")]))
    root.destroy()
    if fileName == "":
        return
    print("> Encriptando: " +fileName)
    fileKey = c.getRandomAESKey()
    c.encryptFile( fileName, fileKey )

    # GENERAR EL ARCHIVO CON LA CLAVE SIMETRICA ENCRIPTADA CON MI PUBLICA
    ownPublicKey = u.getUserListLine( user.index)[2]
    encryptedKey = c.encryptKey( fileKey, ownPublicKey )

    outputFile = u.getUserFileAddr(user) + user.userName + "_" + fileName
    os.makedirs(os.path.dirname(outputFile), exist_ok=True)
    with open(outputFile, 'wb') as outFile:
        outFile.write(encryptedKey)



    return

def decryptFile():
    print("DESENCRIPTAR")
    return False

def newUser( user: u.User ): #toma un parametro solo por compatibilidad
    addUser()
    return False
