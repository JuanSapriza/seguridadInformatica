from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
import gral as g

sha3 = 0
blake2 = 1
hashingAlgorith = sha3
if hashingAlgorith == blake2:
    from Crypto.Hash import BLAKE2b as hash
elif hashingAlgorith == sha3 :
    from Crypto.Hash import SHA3_512 as hash



def encryptFile( file: str, key: bytes) -> bool:
    try:
        g.debug("A ENCRIPTAR " + file )
        g.debug( b"con key " + key )
        g.pause()
        with open(file, "rb") as file_in:
            cipher = AES.new(key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(file_in.read())  # @ToDo: Considerar utilizar MAC tag
        with open(file, "wb") as file_in:
            [file_in.write(x) for x in (cipher.nonce, tag, ciphertext)]
            return True
    except PermissionError:
        print("> Acceso denegado por el SO")
        return False

def decryptFile( file: str, key: bytes ) -> bool:
    try:
        g.debug("A DESENCRIPTAR " + file)
        g.debug(b"con key " + key)
        g.pause()
        with open(file,"rb") as file_in:
            nonce, tag, ciphertext = [file_in.read(x) for x in (16, 16, -1)]
        cipher = AES.new( key, AES.MODE_EAX, nonce )
        data = cipher.decrypt(ciphertext)
        with open(file,"wb") as file_in:
            file_in.write(data)
        return True
    except PermissionError:
        print("> Acceso denegado por el SO")
        return False

def copyDecryptedAndDecoded( file: str, key: bytes ) -> str:
    decryptFile(file, key )
    listFile = open(file, 'rb')
    sFile = listFile.read().decode()
    listFile.close()
    encryptFile(file, key )
    return sFile

def deriveAESkey(psw: str, salt: str) -> bytes:
    return scrypt(psw, salt, max(AES.key_size),2**14,8,1)
# https://pycryptodome.readthedocs.io/en/latest/src/protocol/kdf.html?highlight=pbk#Crypto.Protocol.KDF.PBKDF2

def getRandomAESKey() -> bytes:
    return get_random_bytes( max(AES.key_size))

def hashPsw( psw: bytes, salt: bytes ) -> bytes:
    saltedPsw = salt + psw
    if hashingAlgorith == sha3:
        return hash.new(saltedPsw).digest()
    if hashingAlgorith == blake2:
        h = hash.new(digest_bits=512)
        return h.update(saltedPsw).digest()