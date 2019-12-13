import getpass
import os
from cryptography.fernet import Fernet
import logging
import argparse
import string
import six

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')   

def encrypt_password(key_file, password):
    key = Fernet.generate_key()

    with open(key_file, 'wb') as w:
        w.write(key)

    f = Fernet(key)    

    token = f.encrypt(password.encode())

    return token.decode()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-pass_key_file', help='Pass key file store password key')    
    args = parser.parse_args()

    passKeyFile = args.pass_key_file

    if passKeyFile == None or len(passKeyFile) == 0:
        parser.error("Pass Key File not specified (use -pass_key_file) or is Invalid.")

    print()

    password = getpass.getpass("Please enter password to encrypt: ")
    enc_pass = encrypt_password( os.path.dirname(os.path.abspath(__file__)) + '/resources/' + passKeyFile, password)

    logging.info('Done.')
    logging.info('Encrypted Password: {epassword}'.format(epassword=enc_pass))