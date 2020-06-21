from Crypto.PublicKey import RSA
from Crypto.Random import random as rdm
import encryptionFwk as c
import os
import getpass
from gral import encoding, popUp
import gral as g

# USER LIST
userList = "users.bin"
prefixIndex = b"<IX>"
prefixUserName = b"<UN>"
prefixSalt = b"<ST>"
prefixPassWord = b"<PW>"
prefixRole = b"<RL>"
prefixPrivate = b"<PR>"
prefixPublic = b"<PU>"
userEnd = b"<\n"
lineEnd = b"\n"
prefixes = (prefixIndex,prefixUserName,prefixSalt,prefixPassWord,prefixRole,prefixPrivate,prefixPublic)
userListOrder = (prefixUserName,prefixSalt,prefixPassWord,prefixRole,prefixPublic,prefixIndex,userEnd)
userInfoOrder = (prefixIndex, prefixUserName,prefixRole,prefixPrivate,userEnd)
# USER INFO
sufixUserInfo = "_info.bin"

pswSaltLengthBits = 16
RSAlength = 2048

# DEFAULTS
defaultIndex = -1
defaultBytes = b""
defaultStr = ""

class User:
    def __init__(self, userName: str =defaultStr, salt: bytes=defaultBytes, hPsw: bytes=defaultBytes, role: str=defaultStr, private: bytes=defaultBytes, public: bytes=defaultBytes, AESkey: bytes =defaultBytes, index: int =defaultIndex):
        self.userName = userName
        self.salt = salt
        self.hPsw = hPsw
        self.role = role
        self.private = private
        self.public = public
        self.AESkey = AESkey
        self.index = index

############### CONTROL DE ACCESO ##############
def authorization() -> (User, bool) :
    print(" #### ACCESO AL SISTEMA ####")
    with  open(userList, 'rb') as inFile:
        sFile = inFile.read()
    while True:
        # Obtener Nombre de Usuario
        userName = input("Nombre de Usuario: ")
        if userName == "":
            retriesLogic(True)
            popUp("> Cerrando!")
            return None, False
        userStart = sFile.find(userName.encode(encoding))

        incomplete = sFile[ userStart : sFile.find( userListOrder[userListOrder.index(prefixUserName)+1])].decode(encoding) != userName

        # Si no hubo match  o el match se dio en un lugar que no es un nombre    El nombre ingresado es exactamente to do el nombre que hay guardado
        if userStart < 0 or sFile[userStart-len(prefixUserName):userStart] != prefixUserName or incomplete:
            popUp("> Usuario no existe!")
            continue

        # Obtener contraseña y chequearla
        while retriesLogic(False):
            inPsw = getpass.getpass(prompt="Contraseña: ")
            if inPsw == "":
                retriesLogic(True)
                popUp("> Abortado!")
                return None, False
            inPsw = inPsw.encode(encoding)
            # OBTENER EL SALT
            saltStart = sFile.find(prefixSalt, userStart) + len(prefixSalt)
            saltEnd = sFile.find(userListOrder[userListOrder.index(prefixSalt)+1],saltStart)
            salt = sFile[saltStart:saltEnd]
            # SALTEAR Y HASHEAR LA PSW INGRESADA
            hashedPsw = c.hashPsw( inPsw, salt)
            # OBTENER LA PSW
            storedPswStart = sFile.find(prefixPassWord, userStart) + len(prefixPassWord)
            storedPswEnd = sFile.find(userListOrder[userListOrder.index(prefixPassWord)+1],storedPswStart)
            storedPsw = sFile[storedPswStart:storedPswEnd]
            # COMPARAR PSWs
            if hashedPsw == storedPsw:
                popUp("ACCESO GARANTIZADO")
                retriesLogic(True)
                # OBTENER EL INDICE DEL USUARIO
                indexStart = sFile.find(prefixIndex,userStart) + len(prefixIndex)
                indexEnd = sFile.find(userListOrder[userListOrder.index(prefixIndex)+1],indexStart)
                index = int.from_bytes(sFile[indexStart:indexEnd],'big')
                # CREAR EL USUARIO PARA DEVOLVER
                user = User(userName=userName, AESkey=c.deriveAESkey(str(inPsw.decode(encoding)), str(salt)), index=index)
                return user, True
            else:
                popUp("> Contraseña incorrecta!") #ToDo revisar que no se borre el nombre de usuario cuando le erro de contrasena
        print("ACCESO DENEGADO")
        return None, False

############## LISTA DE USUARIOS  ##############

# En caso de que no haya una tabla, crearla
def generateTable():
    try:
        file_in = open(userList, "rb")
        file_in.close()
    except FileNotFoundError:  # es la primera vez que se ejecuta
        open(userList, "wb").close()
        addUser()

# Solicitar al usuario su informacion
def addUser():
    print(" #### NUEVO USUARIO ####")

    role = input("Ingrese el Rol: ")

    while True:
        invalid = False
        userName = input("Ingrese el nombre de usuario: ")
        # chequear que el nombre de usuario no exista ya!
        i = 0
        while True:
            [uName,*_, uLast] = getUserListLine(i)
            i += 1
            if uName == userName:
                invalid = True
                popUp("> El nombre de usuario ya existe!")
                break
            if uLast:
                break
        if not invalid:
            break
    # Ingreso de Contraseña
    while True:
        password = getpass.getpass("Ingrese contraseña: ")
        checkMsg = pswRequisites(password)
        if checkMsg == True:
            password2 = getpass.getpass("Reingrese contraseña: ")
            if password != password2:
                popUp(" > Contraseñas no coinciden!") #ToDo revisar que no se borre el nombre de usuario cuando le erro de contrasena
                continue
            break
        else:
            popUp(checkMsg)                

    print("GENERANDO USUARIO...")
    generateUser(userName, password, role)

# Con la informacion ingresada genera las claves y lo almacena en la lista de usuarios
def generateUser(userName: str, password: str, role: str):
    # Generación de par de claves
    key = RSA.generate(RSAlength)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    # Salteado de la Password
    salt = rdm.getrandbits(pswSaltLengthBits).to_bytes(2,'big')
    psw = password.encode(encoding)
    hashedPsw = c.hashPsw( psw, salt )
    user = User(userName=userName, salt=salt, hPsw=hashedPsw, role=role, private=private_key, public=public_key)

    # AGREGAR EL NUEVO USUARIO A LA LISTA DE USUARIOS
    with  open(userList, "rb+") as listFile:
        lines = listFile.read().count(prefixIndex)+1  # obtener el numero de usuario
        user.index = lines
        listFile.write(getuserLine(user))

    # CREAR LOS ARCHIVOS Y CARPETS PROPIOS DE CADA USUARIO
    os.makedirs(os.path.dirname(getUserFileAddr(user)), exist_ok=True)
    os.makedirs(os.path.dirname(getuserArchivesAddr(user)), exist_ok=True)
    with open(getUserFileAddr(user), 'wb') as userFile:
        userFile.write(getUserInfo(user))
    c.encryptFile(getUserFileAddr(user), c.deriveAESkey(password, str(salt)))

# Parsea NOMBRE, SALT, HPSW, CLAVE PUBLICA e INDICE para escribir en la lista
def getuserLine(user: User) -> bytes:
    return prefixUserName + user.userName.encode(encoding) \
           + prefixSalt + user.salt \
           + prefixPassWord + user.hPsw \
           + prefixRole + user.role.encode(encoding) \
           + prefixPublic + user.public \
           + prefixIndex + user.index.to_bytes(2, 'big') \
           + userEnd

# Dado un indice, retorna el nombre, rol y clave publica de dicho usuario en la lista
def getUserListLine( index: int ) -> (str, str, bytes, bool):
    with open(userList,'rb') as file:
        sList = file.read()
    # ENCONTRAR EL USUARIO
    uIndex = 0
    nextIndex = 0
    for i in range(index):
        uIndex = sList.find(prefixIndex,nextIndex)
        nextIndex = uIndex + len(prefixIndex)
    if sList.find(userEnd,uIndex)+len(userEnd) == len(sList):
        lastUser = True
    else:
        lastUser = False
    # OBTENER NOMBRE DE USUARIO
    userNameStart = sList.rfind(prefixUserName,0,uIndex) + len(prefixUserName)
    userNameEnd = sList.find(userListOrder[userListOrder.index(prefixUserName)+1],userNameStart)
    userName = sList[userNameStart:userNameEnd].decode(encoding)
    # OBTENER ROL
    roleStart = sList.rfind(prefixRole, 0, uIndex) + len(prefixRole)
    roleEnd = sList.find(userListOrder[userListOrder.index(prefixRole)+1], roleStart)
    role = sList[roleStart:roleEnd].decode(encoding)
    # OBTENER CLAVE PUBLICA
    puStart = sList.rfind(prefixPublic, 0, uIndex) + len(prefixPublic)
    puEnd = sList.find(userListOrder[userListOrder.index(prefixPublic)+1],puStart)
    public = sList[puStart:puEnd]

    return userName, role, public, lastUser



############# ARCHIVO PARTICULAR DE CADA USUARIO: #############

# INDICE, NOMBRE, ROL Y CLAVE PRIVADA
def getUserInfo(user: User) -> bytes:
    return prefixIndex + user.index.to_bytes(2, 'big') + lineEnd \
           + prefixUserName + user.userName.encode(encoding) + lineEnd \
           + prefixRole + user.role.encode(encoding) + lineEnd \
           + prefixPrivate + user.private + userEnd \

# Direccion donde se pueden almacenar archivos para el usuario
def getUserAddr(user: User) -> str:
    return user.userName + "/"

# Direccion y nombre del archivo personal del usuario
def getUserFileAddr(user: User) -> str:
    return getUserAddr(user) + user.userName + sufixUserInfo

def getuserArchivesAddr( user: User ) -> str:
    return getUserAddr(user) + "archivos/"

# ToDo agergar una carpeta de Usuarios
# Dado un usuario, devuelve el rol y clave privada, almacenado en su archivo personal
def getInfoFromUserFile( user: User ) -> User:
    userFile = getUserFileAddr( user )
    if not c.decryptFile(userFile, user.AESkey ):
        return None
    with open( userFile, 'rb') as file:
        file = file.read()
    c.encryptFile(userFile, user.AESkey)
    lUser = user
    # OBTENCION DE ROL
    roleStart = file.find(prefixRole) + len(prefixRole)
    roleEnd = file.find(userInfoOrder[userInfoOrder.index(prefixRole)+1])
    lUser.role = file[roleStart:roleEnd].decode(encoding)
    # OBTENCION DE LA CLAVE PRIVADA
    prStart = file.find(prefixPrivate) + len(prefixPrivate)
    prEnd = file.find(userInfoOrder[userInfoOrder.index(prefixPrivate)+1])
    lUser.private = file[prStart:prEnd]
    return lUser




############## CONTROL DE CONTRASEÑAS #############

def pswRequisites(psw: str): # ToDo Agregar control de usuario
    # largo minimo
    if len(psw) < 10:
        return "Debe tener al menos 10 caracteres"
    # alguna mayuscula
    check = False
    for char in psw:
        if char.isupper():
            check = True
            break
    if not check:
        return "Debe tener al menos 1 mayúscula"
    # alguna minuscula
    check = False
    for char in psw:
        if char.islower():
            check = True
            break
    if not check:
        return "Debe tener al menos 1 minúscula"
    # algun numero
    check = False
    for char in psw:
        if char.isnumeric():
            check = True
            break
    if not check:
        return "Debe tener al menos 1 número"
    # ToDo Implementar!
    '''
    # algun caracter especial
    check = False
    for char in range(len(psw)):
        if char(0x21) <= psw[char] <= char(0x2F):
            check = True
            break
    if not check:
        return False
    '''
    # Al menos 5 caracteres distintos
    chars = []
    for char in psw:
        if char not in chars:
            chars.append(char)
    if len(chars) < 5:
        return "Debe tener al menos 5 caracteres distintos"
    return True

def retriesLogic(reset: bool):
    try:
        retriesLogic.count += 1
    except:
        retriesLogic.count = 0
    if reset:
        retriesLogic.count = 0
        return True
    if retriesLogic.count == 3:
        retriesLogic.count = 0
        return False
    return True
