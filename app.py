import userInfo as u
import menu as m
import gral as g
from gral import popUp


# COMMIT: SE PUEDE COMPARTIR UN ARCHIVO QUE HAYA SIDO YA ENCRIPTADO

print(" #### INICIANDO SISTEMA ####")
u.generateTable()
g.cls()

while True:
    # CONTROL DE ACCESO
    (user, valid) = u.authorization()
    if not valid:
        quit()
    g.cls()

    # CARGAR LA INFORMACION DEL USUARIO QUE ACABA DE INGRESAR
    user = u.getInfoFromUserFile( user )
    if user is None:
        popUp("> MANEJAR ERROR, NO SE PUDO CARGAR LA INFO DEL USUARIO")
        quit()

    # MENU PPAL
    while True:
        if m.showMenu( user ):
            break
    g.cls()
    popUp( " CHAU :D ")
