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

try:
    from project import localsettings as settings
except:
    from project import settings

import passwords
from db_backup import _get_media_filename, _get_dump_filename, _get_enc_filename


def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    """ Decrypts a file using AES (CBC mode) with the
        given key. Parameters are similar to encrypt_file,
        with one difference: out_filename, if not supplied
        will be in_filename without its last extension
        (i.e. if in_filename is 'aaa.zip.enc' then
        out_filename will be 'aaa.zip')
    """
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)


def _download_from_s3(filename):
    s3 = boto.connect_s3(passwords.S3_ACCESS_KEY_ID, passwords.S3_SECRET_KEY)
    key = s3.get_bucket(passwords.S3_BUCKET).get_key(filename)
    key.get_contents_to_filename(filename)


def restore_db(datestring=''):

    if not datestring:
        print "Please include a filename using datestring"
        return

    print "About to restore the database from S3. Are you sure? This will wipe out everything."
    answer = raw_input(">> ").lower()
    if not (answer == "y" or answer == "yes"):
        print "DB Restoration Canceled"
        return

    print "No, seriously. Everything in your database, gone. Are you SURE?!"
    answer = raw_input(">> ").lower()
    if not (answer == "y" or answer == "yes"):
        print "DB Restoration Canceled"
        return

    if not settings.DEBUG:
        print "Cannot run this on production! Please enable DEBUG and retry!"
        return

    print "Restoring database from S3 Backup"

    filename = _get_dump_filename(datestring)
    enc_filename = _get_enc_filename(filename)

    _download_from_s3(enc_filename)
    decrypt_file(passwords.CRYPTO_KEY, enc_filename,  filename)
    local("mysql {1} -uroot -p{0} < ".format(passwords.MYSQL_ROOT_PASSWORD, passwords.MYSQL_DB) + filename)
    local("rm " + enc_filename)
    local("rm " + filename)

    print "Database restored"
    
    media_tar = _get_media_filename(datestring)
    enc_media_tar = _get_enc_filename(media_tar)

    _download_from_s3(enc_media_tar)
    decrypt_file(passwords.CRYPTO_KEY, enc_media_tar,  media_tar)
    local("tar -xvzf {0} -C {1}".format(media_tar, settings.MEDIA_ROOT))
    local("rm " + enc_media_tar)
    local("rm " + media_tar)

    print "Media restored"

    print "Restoration Complete!"


def list_backups():
    s3 = boto.connect_s3(passwords.S3_ACCESS_KEY_ID, passwords.S3_SECRET_KEY)
    bucket = s3.get_bucket(passwords.S3_BUCKET)
    print ""
    print "S3 Bucket Contents:"
    print "-----------"
    print "\n".join([k.key for k in bucket.list()])


def delete_backup(datestring=''):

    if not datestring:
        print "Need a datestring! Aborting!"
        quit()

    print "Are you sure you want to delete this backup? It will be gone forever."
    answer = raw_input(">> ").lower()
    if not (answer == "y" or answer == "yes"):
        print "Delete Canceled."
        return

    s3 = boto.connect_s3(passwords.S3_ACCESS_KEY_ID, passwords.S3_SECRET_KEY)
    bucket = s3.get_bucket(passwords.S3_BUCKET)

    filename = _get_enc_filename(_get_dump_filename(datestring))
    bucket.get_key(filename).delete()

    media_tar = _get_enc_filename(_get_media_filename(datestring))
    bucket.get_key(media_tar).delete()

    print "Removed backup from S3!"

