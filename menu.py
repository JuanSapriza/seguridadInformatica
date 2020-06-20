import gral as g
from gral import popUp,input_timeout
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import encryptionFwk as c
import userInfo as u
from userInfo import addUser, User
import glob, os


def showMenu( user: User ) -> bool:
    g.cls()
    print( "#### MENU PRINCIPAL ####" )
    print("Usuario: " + str(user.index) +" > " + user.userName + " | " + str(user.role) )
    print("   ¿Qué desea hacer? ")
    print(" 1. Encriptar Archivo")
    print(" 2. Desencriptar Archivo")
    print(" 3. Agregar Nuevo Usuario")
    print(" 4. Compartir archivo")
    action = input_timeout(5)

    if action == "":
        return True
    f = function2Perfom(int(action))
    if f is not False:
        f(user)
    return False

# TODO: que se puede encriptar un .txt

########## FUNCIONES DEL MENU PPAL #############

def function2Perfom( index: int ):
    switch = {
        1 :encryptFile,
        2 :decryptFile,
        3 :newUser,
        4: shareFile,
    }
    return switch.get(index,False)

def encryptFile( user: u.User ):
    g.cls()
    print(" #### ENCRIPTAR ARCHIVO ####")
    # OBTENCION DEL ARCHIVO A ENCRIPTAR
    root = Tk()
    root.iconbitmap(r'logoUcu.ico')
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

    encryptKey4Share(user,fileKey,fileName)

    popUp("> Transferencia realizada!")
    return

def decryptFile(user: User):
    g.cls()
    print(" #### DESENCRIPTAR ARCHIVO ####")
    # OBTENCION DEL ARCHIVO A DESENCRIPTAR
    root = Tk()
    root.iconbitmap(r'logoUcu.ico')
    root.wm_withdraw()
    fileDir = askopenfilename(title="Elegir Archivo", filetypes=([("Binarios", "*.bin")]))
    root.destroy()
    if fileDir == "":
        return
    print("> Desencriptando: " +fileDir)
    fileName = fileDir[fileDir.rfind("/")+1:]

    oldWd = os.getcwd() # Respaldar el working directory para reestablecerlo luego
    os.chdir(u.getuserArchivesAddr(user)) # se cambia el working directory para trabajar mas facil con los archivos del usuario
    encryptedKeyFileName = False
    for file in glob.glob("*.bin"):
        # Obtener el nombre de cada archivo del cual tengo la clave
        if file.find(fileName) == len(user.userName)+1: #los nombres de las claves encriptadas son: <nombre Usuario>_<nombre del archivo>.bin
            encryptedKeyFileName = file
            break
    os.chdir(oldWd)  # Se devuelve el WD al oroginal
    if encryptedKeyFileName is False:
        popUp("> NO ES POSIBLE DESENCRIPTAR EL ARCHIVO" )
        return

    # DESENCRIPTAR LA CLAVE
    decryptedKey = decryptKeyFromAddr(user,u.getuserArchivesAddr(user) + encryptedKeyFileName)

    # DESENCRIPTAR EL ARCHIVO
    c.decryptFile(fileDir,decryptedKey)
    popUp("> Archivo desencriptado exitosamente")

    os.chdir(oldWd) # Se devuelve el WD al oroginal
    return

def newUser(user: User):  # toma un parametro solo por compatibilidad
    addUser()
    return

def shareFile(user: User):
    print("#### COMPARTIR ARCHIVO ####")

    # ELEGIR ARCHIVO A COMPARTIR
    oldWd = os.getcwd()  # Respaldar el working directory para reestablecerlo luego
    os.chdir(u.getuserArchivesAddr(
        user))  # se cambia el working directory para trabajar mas facil con los archivos del usuario
    # Obtener el nombre de cada archivo del cual tengo la clave
    print("Seleccione el archivo a compartir")
    files = []
    i = 1
    for file in glob.glob("*.bin"):
        print(str(i) + ". " + file[len(
            user.userName) + 1:-4])  # No mostrar ni el prefijo con el nombre de usuario ni la extension
        files.append(file)
        i += 1
    os.chdir(oldWd)
    file2ShareIndex = input()
    if not file2ShareIndex.isnumeric():
        return
    file2ShareIndex = int(file2ShareIndex) -1
    # DESENCRIPTAR LA CLAVE SIMETRICA DE ESE ARCHIVO, USANDO LA CLAVE PRIVADA DEL USUARIO
    decryptedKey = decryptKeyFromAddr(user, u.getuserArchivesAddr(user) + files[file2ShareIndex])
    # ELEGI DESTINATARIOS Y ENCRIPTARLES UNA COPIA DE LA CLAVE CON SU CLAVE PUBLICA
    encryptKey4Share(user, decryptedKey, files[file2ShareIndex][len(user.userName)+1:])

    popUp("> Transferencia realizada exitosamente!")
    return

######### FUNCIONES AUXILIARES ###############

def getEncryptedKeyAddr( user: User, fileName: str ) -> str:
    return u.getuserArchivesAddr(user) + user.userName + "_" + fileName

def encryptWithPublic( user: User,key: bytes, fileName: bytes):
    encryptedKey = c.encryptKey(key, user.public)
    with open(getEncryptedKeyAddr(user, fileName), 'wb') as outFile:
        outFile.write(encryptedKey)

def selectAddressees(user: User):
    # MOSTRAR LISTA DE USUARIOS PARA DARLES LA CLAVE
    print("Seleccione Usuarios con los que compartir el archivo")
    print("Para seleccionar varios usuarios, ingresar una lista separada por espacios")
    i = 1
    validIndexes = []
    possibleUsers = []
    while True:
        [uName, uRole, uPub, uLast] = u.getUserListLine(i)
        if i != user.index:
            print(str(i) + ". " + uName + ": " + uRole)
            possibleUsers.append(User(userName=uName, role=uRole, public=uPub, index=i))
            validIndexes.append(i)
        i += 1
        if uLast:
            break
    selection = input()
    # Obtener los destinatarios
    tempDest = [int(x) for x in selection.split() if x.isdigit()]  # Obtiene los numeros de lo que se haya ingresado
    if not tempDest:  # si no hay numeros, se va
        return
    tempIndexes = []
    dest = []
    [tempIndexes.append(x) for x in tempDest if x in validIndexes]
    [dest.append(possibleUsers[x]) for x in range(len(possibleUsers)) if possibleUsers[x].index in tempIndexes]
    print(" El archivo se compartirá con:")
    [print(dest[x].userName) for x in range(len(dest))]
    print(" Para confirmar ingrese <ok>")  # ToDo solicitar la contrasena, en vez de ok
    if "ok" not in input().lower():
        return []
    return dest

def encryptKey4Share(user: User, fileKey, fileName):
    dest = selectAddressees(user)
    if not dest:
        return
    for addressee in dest:
        encryptWithPublic(addressee, fileKey,fileName)

def decryptKeyFromAddr(user: User, address):
    with open(address, 'rb') as encryptedKeyFile:
        encryptedKey = encryptedKeyFile.read()
    return c.decryptKey(encryptedKey, user.private)
