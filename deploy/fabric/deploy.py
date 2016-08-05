from fabric.api import run, cd, sudo, get, put, env, local

from project import settings
import passwords

import os
FILE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

USERNAME = passwords.LINUX_USERNAME
USER_PASSWORD = passwords.LINUX_PASSWORD
GIT_PROJECT_NAME = passwords.GIT_PROJECT_NAME
GIT_PROJECT_BRANCH = passwords.GIT_PROJECT_BRANCH
MYSQL_ROOT_PASSWORD = passwords.MYSQL_ROOT_PASSWORD

env.user = USERNAME
env.password = USER_PASSWORD
env.key_filename = 'deploy/fabric/keys/sshkey'

SETUP_DIRECTORY = "/opt/"
CODE_HOME = SETUP_DIRECTORY + GIT_PROJECT_NAME + "/"

DIRECTORIES_TO_CREATE = ()

GITHUB_SSH_URL = passwords.GITHUB_SSH_URL


def test():
    sudo("ls")


def deploy():

    with cd(CODE_HOME):
        
        run("git reset --hard")
        run("git clean -f -d")
        run("git pull")
        run("git checkout {0}".format(GIT_PROJECT_BRANCH))

        sudo('pip install -r requirements.txt')

        sudo("python src/manage.py collectstatic --noinput", user="www-data")

        sudo("python src/manage.py migrate", user="www-data")

    sudo('service uwsgi restart')

def deploy_crontab():
    put( os.path.join(FILE_DIRECTORY, '../crontab'), '/tmp/crontab')
    sudo('crontab < /tmp/crontab')


def setup_server():

    sudo('apt-get update')
    
    sudo("debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password password {0}'".format(MYSQL_ROOT_PASSWORD))
    sudo("debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password_again password {0}'".format(MYSQL_ROOT_PASSWORD))

    # get the programs we'll need
    sudo('apt-get -y install python-setuptools git nginx mysql-server python-mysqldb')
    sudo('apt-get -y install python-pip python-dev build-essential')
    sudo('apt-get -y install libffi-dev libssl-dev libxml2-dev libxslt1-dev')
    sudo('apt-get -y install yui-compressor')
    sudo('apt-get -y build-dep python-imaging') # required for Pillow
    sudo('apt-get -y install libjpeg62 libjpeg62-dev') # required for Pillow
    sudo('apt-get -y install  npm')
    sudo('npm install less -g')
    sudo('apt-get -y install nodejs-legacy node-less')

    sudo('apt-get -y remove uwsgi') # not sure why it's even there on some servers

    sudo('pip install uwsgi')
    sudo('pip install cryptography')
    sudo('pip install pycrypto')

    # get code
    sudo('mkdir -p ' + SETUP_DIRECTORY)
    sudo('chown {0}:www-data '.format(USERNAME) + SETUP_DIRECTORY)
    for d in DIRECTORIES_TO_CREATE:
        sudo('mkdir -p ' + d)
        sudo('chown {0}:www-data '.format(USERNAME) + d)
        sudo('chmod g+w ' + d)

    with cd(SETUP_DIRECTORY):

        for command in _get_configure_db_commands(MYSQL_ROOT_PASSWORD):
            run(command)

        run('[ -d {0} ] || git clone '.format(GIT_PROJECT_NAME) + GITHUB_SSH_URL)
    
        put('{0}/nginx-default-conf'.format(os.path.dirname(FILE_DIRECTORY)), '/etc/nginx/sites-enabled/default', use_sudo=True)
        put('{0}/nginx-conf'.format(os.path.dirname(FILE_DIRECTORY)), '/etc/nginx/nginx.conf', use_sudo=True)
        put('{0}/uwsgi-systemd'.format(os.path.dirname(FILE_DIRECTORY)), '/etc/systemd/system/uwsgi.service', use_sudo=True)
        put('{0}/uwsgi-conf'.format(os.path.dirname(FILE_DIRECTORY)), '/etc/init/uwsgi.conf', use_sudo=True)

        sudo('[ -d `command -v systemctl` ] || systemctl daemon-reload') # run systemctl only if it exists

    sudo('mkdir -p /opt/staticfiles')
    sudo('chown www-data:www-data /opt/staticfiles')
    sudo('mkdir -p /opt/media')
    sudo('chown www-data:www-data /opt/media')

    sudo('mkdir -p /var/log/django/')
    sudo('chown www-data:www-data /var/log/django/')
    sudo('touch /var/log/django/django.log')
    sudo('chown www-data:www-data /var/log/django/django.log')
    sudo('chmod g+w /var/log/django/')
    sudo('service nginx restart')

    put_passwords_file()

    # deploy_crontab()

    deploy()

def create_superuser():

    with cd(CODE_HOME):
        sudo("python src/manage.py createsuperuser", user="www-data")

def tail_log():

    with cd(CODE_HOME):

        sudo("tail -n100 /var/log/django/django.log", user="www-data")

def put_passwords_file():
    passwords_path = os.path.join(FILE_DIRECTORY, '..', '..', 'passwords.py')
    put(passwords_path, "/opt")


def _put_key_file(localkeyname):
    localpath = os.path.join(FILE_DIRECTORY, 'keys', localkeyname)
    print "THIS IS THE KEY: " + localpath
    put(localpath, '/home/{0}/.ssh/'.format(USERNAME))
    sudo('chmod 600 /home/{0}/.ssh/{1}'.format(USERNAME, localkeyname))


def _get_configure_db_commands(root_password):
    # configure our db
    username = settings.DATABASES['default']['USER']
    db = settings.DATABASES['default']['NAME']
    password = settings.DATABASES['default']['PASSWORD']

    if root_password:
        root_password = "-p" + root_password

    commands = (
        "mysql -uroot {0} -e 'CREATE DATABASE IF NOT EXISTS {1}'".format(root_password, db),
        "mysql -uroot {0} -e 'GRANT ALL PRIVILEGES ON {2}.* TO {3}@localhost IDENTIFIED BY \"{1}\"'".format(root_password,password, db, username),
        "mysql -uroot {0} -e 'FLUSH PRIVILEGES'".format(root_password),
    )
    return commands


def configure_local_db(root_password=""):

    for command in _get_configure_db_commands(root_password):
        local(command)

    print "MySQL configured successfully!"
