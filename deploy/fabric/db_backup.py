import os, random, struct, datetime
from Crypto.Cipher import AES
from fabric.api import run, cd, sudo, get, put, env, local

import sys
import boto

FILE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
SRC_DIRECTORY = os.path.join(FILE_DIRECTORY, "../../src/")

if SRC_DIRECTORY not in sys.path:
    sys.path.append(SRC_DIRECTORY)

# for the passwords file
if "/opt/" not in sys.path:
    sys.path.append("/opt/")

from project import settings
import passwords

DIRECTORY = "/tmp/"


def _get_media_filename(datestring):
    return DIRECTORY + "media." + datestring + ".tar.gz"


def _get_dump_filename(datestring):
    return DIRECTORY + "dump." + datestring + ".sql"


def _get_enc_filename(filename):
    return filename + ".enc"


def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
    """
    http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/

    Encrypts a file using AES (CBC mode) with the
        given key.

        key:
            The encryption key - a string that must be
            either 16, 24 or 32 bytes long. Longer keys
            are more secure.

        in_filename:
            Name of the input file

        out_filename:
            If None, '<in_filename>.enc' will be used.

        chunksize:
            Sets the size of the chunk which the function
            uses to read and encrypt the file. Larger chunk
            sizes can be faster for some files and machines.
            chunksize must be divisible by 16.
    """
    if not out_filename:
        out_filename = in_filename + '.enc'

    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))


def _upload_to_s3(filename):
    s3 = boto.connect_s3(passwords.S3_ACCESS_KEY_ID, passwords.S3_SECRET_KEY)
    bucket = s3.get_bucket(passwords.S3_BUCKET)

    key = bucket.new_key(filename)
    key.set_contents_from_filename(filename)


def backup_db():

    print "Beginning Backup"

    now = datetime.datetime.now().strftime("%Y-%m-%d.%H-%M")
    filename = _get_dump_filename(now)
    enc_filename = _get_enc_filename(filename)

    local("touch {0}".format(filename))
    local("rm {0}".format(filename))
    local("mysqldump {1} -uroot -p{0} > ".format(passwords.MYSQL_ROOT_PASSWORD, passwords.MYSQL_DB) + filename)
    encrypt_file(passwords.CRYPTO_KEY, filename,  enc_filename)

    _upload_to_s3(enc_filename)
    local("rm " + filename)
    local("rm " + enc_filename)

    print "Database backed up successfully"

    media_tar = _get_media_filename(now)
    enc_media_tar = _get_enc_filename(media_tar)
    local("tar --exclude='{2}' -cvzf {0} -C {1} .".format(media_tar, settings.MEDIA_ROOT, "tempfiles/"))
    encrypt_file(passwords.CRYPTO_KEY, media_tar,  enc_media_tar)

    _upload_to_s3(enc_media_tar)
    local("rm " + media_tar)
    local("rm " + enc_media_tar)

    print "Media folder backed up successfully"

    print "Backup successful!"
    print ""


