from Crypto.PublicKey import RSA
from Crypto.Random import random as rdm
import encryptionFwk as c
import os
import getpass
import gral as g
encoding = 'utf-8'

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
userListOrder = (prefixUserName,prefixSalt,prefixPassWord,prefixPublic,prefixIndex,userEnd)
userInfoOrder = (prefixIndex, prefixUserName,prefixRole,prefixPrivate,lineEnd)

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
            print("> Abortado!")
            return None, False
        userPos = sFile.find(userName.encode(encoding))

        if userPos < 0:
            print("> Usuario no existe!")
            continue

        # Obtener contraseña y chequearla
        while retriesLogic(False):
            inPsw = getpass.getpass(prompt="Contraseña: ")
            if inPsw == "":
                retriesLogic(True)
                print("> Abortado!")
                return None, False
            inPsw = inPsw.encode(encoding)
            # OBTENER EL SALT
            saltStart = sFile.find(prefixSalt, userPos) + len(prefixSalt)
            saltEnd = sFile.find(userListOrder[userListOrder.index(prefixSalt)+1],saltStart)
            salt = sFile[saltStart:saltEnd]
            # SALTEAR Y HASHEAR LA PSW INGRESADA
            hashedPsw = c.hashPsw( inPsw, salt)
            # OBTENER LA PSW
            storedPswStart = sFile.find(prefixPassWord, userPos) + len(prefixPassWord)
            storedPswEnd = sFile.find(userListOrder[userListOrder.index(prefixPassWord)+1],storedPswStart)
            storedPsw = sFile[storedPswStart:storedPswEnd]
            # COMPARAR PSWs
            if hashedPsw == storedPsw:
                print("ACCESO GARANTIZADO")
                retriesLogic(True)
                # OBTENER EL INDICE DEL USUARIO
                indexStart = sFile.find(prefixIndex,userPos) + len(prefixPassWord)
                indexEnd = sFile.find(userListOrder[userListOrder.index(prefixIndex)+1],indexStart)
                index = int.from_bytes(sFile[indexStart:indexEnd],'big')
                # CREAR EL USUARIO PARA DEVOLVER
                user = User(userName=userName, AESkey=c.deriveAESkey(str(inPsw.decode(encoding)), str(salt)), index=index)
                return user, True
            else:
                print("> Contraseña incorrecta!")
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
        generateUser("ml", "mp", "MAdmin")

# Solicitar al usuario su informacion
def addUser():
    print(" #### NUEVO USUARIO ####")

    role = input("Ingrese el Rol: ")
    # @ToDo: chequear que el rol exista

    userName = input("Ingrese el nombre de usuario: ")
    # @ToDo: chequear que el nombre de usuario no exista ya!

    # Ingreso de Contraseña
    while True:
        password = input("Ingrese contraseña: ")
        password2 = input("Reingrese contraseña: ")
        if password != password2:
            print(" > Contraseñas no coinciden!")
            continue
        checkMsg = pswRequisites(password)
        if checkMsg == True:
            break
        else:
            print(checkMsg)

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
        lines = 0  # obtener el numero de usuario
        for line in listFile:
            lines += 1
        user.index = lines
        listFile.write(getuserLine(user))

    # CREAR LOS ARCHIVOS PROPIOS DE CADA USUARIO
    os.makedirs(os.path.dirname(getUserFileAddr(user)), exist_ok=True)
    with open(getUserFileAddr(user), 'wb') as userFile:
        userFile.write(getUserInfo(user))
    c.encryptFile(getUserFileAddr(user), c.deriveAESkey(password, str(salt)))

# Parsea NOMBRE, SALT, HPSW, CLAVE PUBLICA e INDICE para escribir en la lista
def getuserLine(user: User) -> bytes:
    return prefixUserName + user.userName.encode(encoding) \
           + prefixSalt + user.salt \
           + prefixPassWord + user.hPsw \
           + prefixPublic + user.public \
           + prefixIndex + user.index.to_bytes(2, 'big') \
           + userEnd

# Dado un indice, retorna el nombre, rol y clave publica de dicho usuario
def getUserListLine( index: int ) -> (str, str, bytes): #ESTA FUNCION DEVUELVE TO DO VACIO!!
    with open(userList,'rb') as file:
        sList = file.read()
    uIndex = 0
    for i in range(index):
        uIndex = sList.find(prefixIndex)
    # OBTENER NOMBRE DE USUARIO
    userNameStart = sList.rfind(prefixUserName,0,uIndex)
    userNameEnd = userNameStart + sList.find(userListOrder[userListOrder.index(prefixUserName)+1],userNameStart,uIndex)
    userName = sList[userNameStart:userNameEnd]
    # OBTENER ROL
    roleStart = sList.rfind(prefixRole, 0, uIndex)
    roleEnd = roleStart + sList.find(userListOrder[userListOrder.index(prefixRole)+1], roleStart, uIndex)
    role = sList[roleStart:roleEnd]
    # OBTENER CLAVE PUBLICA
    puStart = sList.rfind(prefixPublic, 0, uIndex)
    puEnd = puStart + sList.find(userListOrder[userListOrder.index(prefixPublic)+1],puStart, uIndex)
    public = sList[puStart:puEnd]

    return userName, role, public

############# ARCHIVO PARTICULAR DE CADA USUARIO: #############

# INDICE, NOMBRE, ROL Y CLAVE PRIVADA
def getUserInfo(user: User) -> bytes:
    return prefixIndex + user.index.to_bytes(2, 'big') + lineEnd \
           + prefixUserName + user.userName.encode(encoding) + lineEnd \
           + prefixRole + user.role.encode(encoding) + lineEnd \
           + prefixPrivate + user.private + lineEnd \

# Direccion donde se pueden almacenar archivos para el usuario
def getUserAddr(user: User) -> str:
    return user.userName + "/"

# Direccion y nombre del archivo personal del usuario
def getUserFileAddr(user: User) -> str:
    return getUserAddr(user) + user.userName + sufixUserInfo

# Dado un usuario, devuelve el rol y clave privada, almacenado en su archivo personal
def getInfoFromUserFile( user: User ) -> User:
    userFile = getUserFileAddr( user )
    if not c.decryptFile(userFile, user.AESkey ):
        return None
    with open( userFile, 'rb') as file:
        file = file.read()
    lUser = user
    # OBTENCION DE ROL
    roleStart = file.find(prefixRole)
    roleEnd = roleStart + file[roleStart:].find(lineEnd)
    lUser.role = file[roleStart:roleEnd]
    # OBTENCION DE LA CLAVE PRIVADA
    prStart = file.find(prefixPrivate)
    prEnd = prStart + file[prStart:].find(lineEnd)
    lUser.private = file[prStart:prEnd]
    return lUser

############## CONTROL DE CONTRASEÑAS #############

def pswRequisites(psw: str):
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


