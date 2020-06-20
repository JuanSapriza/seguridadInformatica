import userInfo as u
import menu as m
import gral as g


# COMMIT: SE PUEDEN ENCRIPTAR, COMPARTIR (AL MOMENTO DE COMPARTIR) Y DESENCRIPTAR

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

