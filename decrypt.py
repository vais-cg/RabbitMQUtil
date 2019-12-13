import getpass
import os
from cryptography.fernet import Fernet
import logging

import argparse
import string
import six

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')   

def decrypt_password(key_file, enc_pass):
    with open(key_file, 'rb') as r:
        key=r.read()

    f = Fernet(key) 

    decryptPassword = f.decrypt(enc_pass)

    return decryptPassword.decode()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-pass_key_file', help='Pass key file store password key')    
    args = parser.parse_args()

    passKeyFile = args.pass_key_file

    if passKeyFile == None or len(passKeyFile) == 0:
        parser.error("Pass Key File not specified (use -pass_key_file) or is Invalid.")

    print()
    abs_path = os.path.dirname(os.path.abspath(__file__))
    
    enc_password = getpass.getpass("Please enter password to decrypt: ")

    dec_pass = decrypt_password(abs_path + '/resources/' + passKeyFile, enc_password.encode())

    logging.info('Done.')
    logging.info('Decrypted Password: {dpassword}'.format(dpassword=dec_pass))    