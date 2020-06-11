import masterKey as master
import userInfo as user
import encryptionFwk as cript

# ACCEDER AL PROGRAMA
# masterKey = master.masterAccess()

# ESTE ES UN MENSAJE DE PRUEBA!

masterKey = b"estaEsLaMaster151719212325272931"

user.generateTable(masterKey)
while True:
    if user.authorization(masterKey):
        break




#user.addUser(masterKey)

#cript.decryptFile('users.bin',masterKey)
'''
file = open("archivo.bin","wb")
file.write(b"hola esto es una prueb")
file.close()

file = open("archivo.bin","rb")
print("Inicial")
print(file.read())
file.close()

cript.encryptFile("archivo.bin", b"estaEsLaMaster151719212325272931" )

file = open("archivo.bin","rb")
print("Encriptado")
print(file.read())
file.close()

cript.decryptFile("archivo.bin", b"estaEsLaMaster151719212325272931")

file = open("archivo.bin","rb")
print("Final")
print(file.read())
file.close()
'''

