from Crypto.Hash import SHA256 as hash
from Crypto.Random import random

# @ToDo: COMO HACER PARA QUE NO NOS BORREN EL ASTERKEY.BIN???

def masterAccess():
    generateMaster()
    while True:
        masterKeyIn = input("Enter Master Key: ")
        if checkMasterKey(masterKeyIn):
            retriesLogic(True)
            return masterKeyIn
        elif retriesLogic(False) == False:
            print("BLOQUEADO")  # @ToDo: Que hacemos aqui?
            return False


def generateMaster():
    try:
        file_in = open("masterKey.txt","rb")
        file_in.close()
    except FileNotFoundError: # solamente crear una masterKey si no existe una ya.
        plainMaster = "estaEsLaMaster151719212325272931"
        salt = str(random.getrandbits(16))
        saltedMaster = (plainMaster + salt).encode('utf-8') #para hashear, se necesita codificado ('bytes')
        hashedMaster = hash.new(saltedMaster)
        hashedMaster = str(hashedMaster.hexdigest())
        print(hashedMaster)
        file_out = open("masterKey.txt", "w")
        file_out.write("salt: "+ salt + "\n"+"hashed: "+ hashedMaster)
        file_out.close()

def checkMasterKey( input: str ):
    try:
        file_in = open("masterKey.txt","r")
        file = file_in.read()
        file_in.close()

        saltHead = "salt: "
        saltTail = "\n"
        hashHead = "hashed: "

        salt = file[ file.find(saltHead) + len(saltHead): file.find(saltTail) ]
        hashedMaster = file[ file.find(hashHead) + len(hashHead) :]

        saltedTry = ( input + salt ).encode('utf-8')
        hashedTry = hash.new(saltedTry)
        if hashedTry.hexdigest() == hashedMaster:
            print(" #### ACCESO GARANTIZADO ####")
            return True
        else:
            print(" #### ACCESO DENEGADO ####")
            return False
    except FileNotFoundError:
        print("ERROR!")

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