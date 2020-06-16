import userInfo as u
import menu as m
import gral as g


'''

import encryptionFwk as cript

g.pause()
cript.encryptFile('ml_info.bin', cript.deriveAESkey("hola","chau"))
g.pause()
cript.decryptFile('ml_info.bin',cript.deriveAESkey("hola","chau"))

'''

# JOACO PUTO

print(" #### INICIANDO SISTEMA ####")
u.generateTable()
g.cls()

# CONTROL DE ACCESO
(user, valid) = u.authorization()
if not valid:
    quit()
g.cls()

user = u.getInfoFromUserFile( user )
if user is None:
    print("> MANEJAR ERROR, NO SE PUDO CARGAR LA INFO DEL USUARIO")
    quit()

# MENU PPAL
while True:
    if m.showMenu( user ):
        break
g.cls()

print( " CHAU :D ")

#'''
