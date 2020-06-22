from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
import gral as g

mode = AES.MODE_GCM

sha3 = 0
blake2 = 1
hashingAlgorith = sha3
if hashingAlgorith == blake2:
    from Crypto.Hash import BLAKE2b as hash
elif hashingAlgorith == sha3 :
    from Crypto.Hash import SHA3_512 as hash


def encryptFile( file: str, key: bytes) -> bool:
    try:
        with open(file, "rb") as file_in:
            cipher = AES.new(key, mode)
            ciphertext, tag = cipher.encrypt_and_digest(file_in.read())
        with open(file, "wb") as file_in:
            [file_in.write(x) for x in (cipher.nonce, tag, ciphertext)]
            return True
    except PermissionError:
        print(" > Acceso denegado por el SO")
        return False

def decryptFile( file: str, key: bytes ) -> bool:
    try:
        with open(file,"rb") as file_in:
            nonce, tag, ciphertext = [file_in.read(x) for x in (16, 16, -1)]
        cipher = AES.new( key, mode, nonce )
        data = cipher.decrypt(ciphertext) # ToDo considerar agregar el tag
        with open(file,"wb") as file_in:
            file_in.write(data)
        return True
    except PermissionError:
        print(" > Acceso denegado por el SO")
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

def getRandomAESKey() -> bytes:
    return get_random_bytes( max(AES.key_size))

def encryptKey( key: bytes, public: bytes ) -> bytes:
    cipher_key = RSA.importKey(public)
    cipher_rsa = PKCS1_OAEP.new(cipher_key)
    return cipher_rsa.encrypt(key)

def decryptKey( key: bytes, private: bytes ) -> bytes:
    cipher_key = RSA.importKey(private)
    cipher_rsa = PKCS1_OAEP.new(cipher_key)
    return cipher_rsa.decrypt(key)

def hashPsw( psw: bytes, salt: bytes ) -> bytes:
    saltedPsw = salt + psw
    if hashingAlgorith == sha3:
        return hash.new(saltedPsw).digest()
    if hashingAlgorith == blake2:
        h = hash.new(digest_bits=512)
        return h.update(saltedPsw).digest()
