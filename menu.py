import gral as g
from gral import encoding
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import encryptionFwk as c
import userInfo as u



def showMenu( user: u.User ) -> bool:
    #g.cls()
    print( "#### MENU PRINCIPAL ####" )
    print("Usuario: " + str(user.index) +" > " + user.userName + " | " + str(user.role) )
    print("   ¿Qué desea hacer? ")
    print(" 1. Encriptar Archivo")
    print(" 2. Desencriptar Archivo")
    print(" 3. Agregar Nuevo Usuario")
    action = input()
    if action == "":
        return True
    function2Perfom(int(action))(user)
    return False

def function2Perfom( index: int ):
    switch = {
        1 :encryptFile,
        2 :decryptFile,
        3 :newUser,
    }
    return switch.get(index,False)

def encryptFile( user: u.User ):
    g.cls()
    print(" #### ENCRIPTAR ARCHIVO ####")
    root = Tk()
    root.wm_withdraw()
    fileName = askopenfilename(title="Elegir Archivo", filetypes=([("Binarios", "*.bin")]))
    root.destroy()
    if fileName == "":
        return
    print("> Encriptando: " +fileName)
    fileKey = c.getRandomAESKey()
    c.encryptFile( fileName, fileKey )

    publicKey = u.getUserListLine( user.index )

    print( publicKey )

    return

def decryptFile():
    print("DESENCRIPTAR")
    return False

def newUser():
    print("USER")
    return False
