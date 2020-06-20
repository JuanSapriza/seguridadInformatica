import gral as g
from gral import encoding
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import encryptionFwk as c
import userInfo as u
from userInfo import addUser
from userInfo import User
import glob, os

def showMenu( user: User ) -> bool:
    #g.cls()
    print( "#### MENU PRINCIPAL ####" )
    print("Usuario: " + str(user.index) +" > " + user.userName + " | " + str(user.role) )
    print("   ¿Qué desea hacer? ")
    print(" 1. Encriptar Archivo")
    print(" 2. Desencriptar Archivo")
    print(" 3. Agregar Nuevo Usuario")
    print(" 4. Compartir archivo")
    action = input()
    if action == "":
        return True
    f = function2Perfom(int(action))
    if f is not False:
        f(user)
    return False

def function2Perfom( index: int ):
    switch = {
        1 :encryptFile,
        2 :decryptFile,
        3 :newUser,
        4: shareFile,
    }
    return switch.get(index,False)


# TODO: que se puede encriptar un .txt

def encryptFile( user: u.User ):
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

    print("> Archivo encriptado exitosamente!")

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
    selection = input()
    # Obtener los destinatarios
    tempDest = [int(x) for x in selection.split() if x.isdigit()] #Obtiene los numeros de lo que se haya ingresado
    if not tempDest: # si no hay numeros, se va
        return
    tempIndexes = []
    dest = []
    [ tempIndexes.append(x) for x in tempDest if x in validIndexes ]
    [dest.append(possibleUsers[x]) for x in range(len(possibleUsers)) if possibleUsers[x].index in tempIndexes]
    print(" El archivo se compartirá con:")
    [ print(dest[x].userName) for x in range(len(dest)) ]
    print(" Para confirmar ingrese <ok>")
    if "ok" not in input().lower():
        return

    # CREAR LA CLAVE ENCRIPTADA PARA LOS USUARIOS A COMPARTIR
    for addressee in dest:
        addrPublicKey = addressee.public
        encryptedKey = c.encryptKey(fileKey, addrPublicKey)
        with open(getEncryptedKeyAddr(addressee, fileName), 'wb') as outFile:
            outFile.write(encryptedKey)

    print("> Transferencia realizada!")
    return

def getEncryptedKeyAddr( user: User, fileName: str ) -> str:
    return u.getuserArchivesAddr(user) + user.userName + "_" + fileName

def decryptFile(user: User):
    g.cls()
    print(" #### DESENCRIPTAR ARCHIVO ####")
    # OBTENCION DEL ARCHIVO A DESENCRIPTAR
    root = Tk()
    root.wm_withdraw()
    fileDir = askopenfilename(title="Elegir Archivo", filetypes=([("Binarios", "*.bin")]))
    root.destroy()
    if fileDir == "":
        return
    print("> Desencriptando: " +fileDir)
    fileName = fileDir[fileDir.rfind("/")+1:]

    oldWd = os.getcwd() # Respaldar el working directory para reestablecerlo luego
    os.chdir(u.getuserArchivesAddr(user)) # se cambia el working directory para trabajar mas facil con los archivos del usuario
    encryptedKeyFileAddr = False
    for file in glob.glob("*.bin"):
        # Obtener el nombre de cada archivo del cual tengo la clave
        if file.find(fileName) == len(user.userName)+1: #los nombres de las claves encriptadas son: <nombre Usuario>_<nombre del archivo>.bin
            encryptedKeyFileAddr = file
            break
    if encryptedKeyFileAddr is False:
        print("> NO ES POSIBLE DESENCRIPTAR EL ARCHIVO" )
        os.chdir(oldWd) # Se devuelve el WD al oroginal
        return

    # DESENCRIPTAR LA CLAVE
    with open(encryptedKeyFileAddr,'rb') as encryptedKeyFile:
        encryptedKey = encryptedKeyFile.read()
    decryptedKey = c.decryptKey(encryptedKey,user.private)

    # DESENCRIPTAR EL ARCHIVO
    c.decryptFile(fileDir,decryptedKey)
    print("> Archivo desencriptado exitosamente")

    os.chdir(oldWd) # Se devuelve el WD al oroginal
    return

def newUser( user: User ): #toma un parametro solo por compatibilidad
    addUser()
    return

def shareFile(user: User):
    print("COMPARTIR ARCHIVO")

    return
