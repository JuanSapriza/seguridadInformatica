from Crypto.PublicKey import RSA
import encryptionFwk as cript
import masterKey as mk

userList = "users.bin"

prefixUserName = "UN>"
prefixPassWord = "<PW>"
prefixRole = "<RL>"
prefixPrivate = "<PR>"
prefixPublic = "<PU>"
userEnd = "<\n"


class User:
    def __init__(self, userName: str, psw: str, role: str, private: str, public: str):
        self.userName = userName
        self.psw = psw
        self.role = role
        self.private = private
        self.public = public


def authorization(MK: bytes) -> bool:  # @ToDo: hashear nombre de usuario, contrasena y rol
    print(" #### ACCESO AL SISTEMA ####")
    sFile = cript.copyDecryptedAndDecoded( userList, MK)
    while True:
        userName = input("Nombre de Usuario: ")
        if userName == "":
            mk.retriesLogic(True)
            print("> Abortado!")
            return False
        userNamePos = sFile.find(userName)
        if userNamePos < 0:
            print("> Usuario no existe!")
            continue
        while mk.retriesLogic(False):
            psw = input("Contraseña: ")
            if psw == "":
                mk.retriesLogic(True)
                print("> Abortado!")
                return False
            pswStart = sFile.find(prefixPassWord) + len(prefixPassWord)
            if psw == sFile[pswStart:pswStart+len(psw)]:
                print( "ACCESO GARANTIZADO" )
                mk.retriesLogic(True)
                return True
            else:
                print( "> Contraseña incorrecta!" )
        print( "ACCESO DENEGADO" )
        return False



def generateTable(MK: bytes):
    try:
        file_in = open(userList, "rb")
        file_in.close()
    except FileNotFoundError:  # es la primera vez que se ejecuta
        open(userList, "wb").close()
        cript.encryptFile(userList, MK)
        generateUser("masterAdmin", "masterPassword", "MAdmin", MK)


def addUser(MK: bytes):
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
    generateUser( userName, password, role, MK)


def generateUser(userName: str, password: str, role: str, MK: bytes):
    # Generación de par de claves
    key = RSA.generate(2048)
    private_key = key.export_key().decode('Latin-1')
    public_key = key.publickey().export_key().decode('Latin-1')

    user = User(userName, password, role, private_key, public_key)

    cript.decryptFile(userList, MK)
    listFile = open(userList, "ab")
    listFile.write(getuserLine(user).encode('utf-8'))
    listFile.close()
    cript.encryptFile(userList, MK)


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


def getuserLine(user: User) -> str:
    return prefixUserName + user.userName + prefixPassWord + user.psw + prefixRole + user.role + prefixPrivate + user.private + prefixPublic + user.public + userEnd
