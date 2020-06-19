import gral as g
from gral import encoding
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import encryptionFwk as c
import userInfo as u
from userInfo import addUser
from userInfo import User
import os

def showMenu( user: User ) -> bool:
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

def encryptFile( user: User ):
    g.cls()
    print(" #### ENCRIPTAR ARCHIVO ####")
    # OBTENCION DEL ARCHIVO A ENCRIPTAR
    root = Tk()
    root.wm_withdraw()
    fileDir = askopenfilename(title="Elegir Archivo", filetypes=([("Binarios", "*.bin")]))
    root.destroy()
    if fileDir == "":
        return
    print("> Encriptando: " +fileDir)
    fileName = fileDir[fileDir.rfind("/")+1:]

    # ENCRIPTAR EL ARCHIVO CON UNA CLAVE ALEATORIA
    fileKey = c.getRandomAESKey()
    c.encryptFile( fileDir, fileKey )

    # GENERAR EL ARCHIVO CON LA CLAVE SIMETRICA ENCRIPTADA CON MI PUBLICA
    ownPublicKey = u.getUserListLine( user.index)[2]
    encryptedKey = c.encryptKey( fileKey, ownPublicKey )

    # GUARDAR UNA COPIA DEL ARCHIVO CIFRADA CON LA CLAVE PUBLICA DEL AUTOR
    with open(getEncryptedKeyAddr(user, fileName), 'wb') as outFile:
        outFile.write(encryptedKey)

    # MOSTRAR LISTA DE USUARIOS PARA DARLES LA CLAVE
    print( "Seleccione Usuarios con los que compartir el archivo" )
    print( "Para seleccionar varios usuarios, ingresar una lista separada por espacios")
    i = 1
    validIndexes=[]
    possibleUsers = []
    while True:
        [uName, uRole, uPub, uLast] = u.getUserListLine(i)
        if i != user.index:
            print( str(i) + ". " + uName + ": " + uRole )
            possibleUsers.append(User(userName=uName,role=uRole, public=uPub, index=i))
            validIndexes.append(i)
        i += 1
        if uLast:
            break
    g.debug(validIndexes)
    selection = input()
    # Obtener los destinatarios
    tempDest = [int(x) for x in selection.split() if x.isdigit()] #Obtiene los numeros de lo que se haya ingresado
    g.debug(tempDest)
    if not tempDest: # si no hay numeros, se va
        return
    tempIndexes = []
    dest = []
    [ tempIndexes.append(x) for x in tempDest if x in validIndexes ]
    [dest.append(possibleUsers[x]) for x in range(len(possibleUsers)) if possibleUsers[x].index in tempIndexes]
    print(" Confirma que desea compartir con ")
    [ print(dest[x].userName) for x in range(len(dest)) ]
    input()
    return

def getEncryptedKeyAddr( user: User, fileName: str ) -> str:
    return u.getuserArchivesAddr(user) + user.userName + "_" + fileName


def decryptFile():
    print("DESENCRIPTAR")

    #decryptedKey = c.decryptKey(encryptedKey, user.private)
    return

def newUser( user: u.User ): #toma un parametro solo por compatibilidad
    addUser()
    return
