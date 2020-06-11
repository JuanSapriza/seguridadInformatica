from Crypto.Cipher import AES


def encryptFile( file: str, key: bytes):
    file_in = open(file, "rb")
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(file_in.read())  # @ToDo: Considerar utilizar MAC tag
    file_in.close()
    file_in = open(file, "wb")
    [file_in.write(x) for x in (cipher.nonce, tag, ciphertext)]
    file_in.close()


def decryptFile( file: str, key: bytes ):
    file_in = open(file,"rb")
    nonce, tag, ciphertext = [file_in.read(x) for x in (16, 16, -1)]
    file_in.close()
    cipher = AES.new( key, AES.MODE_EAX, nonce )
    data = cipher.decrypt(ciphertext)
    file_in = open(file,"wb")
    file_in.write(data)
    file_in.close()

def copyDecryptedAndDecoded( file: str, key: bytes ) -> str:
    decryptFile(file, key )
    listFile = open(file, 'rb')
    sFile = listFile.read().decode()
    listFile.close()
    encryptFile(file, key )
    return sFile