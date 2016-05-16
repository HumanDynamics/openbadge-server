from fabric.api import run, cd, sudo, get, put, env, local

import os
FILE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

from deploy import USERNAME, USER_PASSWORD

env.use_ssh_config = True
env.user = None
env.password = None
env.key_filename = None

HOSTS_FILE = "/home/{0}/.hosts".format(USERNAME)

SSH_KEY_PATH = "{0}/keys/sshkey".format(FILE_DIRECTORY)

def create():
    sudo("id -u {0} &>/dev/null || useradd -m {0} ".format(USERNAME))
    sudo('passwd -d {0}'.format(USERNAME))
    sudo('echo -e "{0}\\n{0}" | sudo passwd {1}'.format(USER_PASSWORD, USERNAME))
    sudo("chsh -s /bin/bash {0}".format(USERNAME))
    sudo("adduser {0} www-data".format(USERNAME))
    sudo("adduser {0} sudo".format(USERNAME))
    add_key(create_ssh_key())
    sudo('if ! cat {1} | grep "Match User {0}"; then echo "\nMatch User {0}\nPasswordAuthentication no" >> {1}; fi;'.format(USERNAME, "/etc/ssh/sshd_config"))
    BASH_PROFILE = "/home/"+USERNAME+"/.profile"
    sudo("touch " + BASH_PROFILE)
    sudo('if ! cat {1} | grep "#Add password"; then printf \'\n\n\n#Add password to pythonpath\nexport PYTHONPATH=$PYTHONPATH:/opt/\' >> {1}; fi;'.format(USERNAME, BASH_PROFILE))
    sudo("chown {0}:{0} {1}".format(USERNAME, BASH_PROFILE))

    sudo("service ssh restart")

def create_ssh_key(keypath=SSH_KEY_PATH):
    local("mkdir -p {0}/keys".format(FILE_DIRECTORY))
    if not os.path.isfile(keypath):
        local("ssh-keygen -b 2048 -t rsa -f {0} -q -N \"\"".format(keypath))

        print "Created SSH Key at: " + keypath

    return keypath + ".pub"

def _get_public_key(key_file):

    with open(os.path.expanduser(key_file)) as fd:
        key = fd.read().strip()
    return key

def add_key(filename, username=USERNAME):

    ssh_home = "/home/{0}/.ssh".format(username)

    auth_keys = ssh_home + "/authorized_keys"

    key_content = _get_public_key(filename)

    commands = (
        "mkdir -p {0};".format(ssh_home),
        "chown {0} {1};".format(username, ssh_home),
        "chmod 700 {0};".format(ssh_home),
        'if ! cat {1} | grep "ssh-rsa"; then echo "{0}" >> {1}; fi;'.format(key_content, auth_keys),
        "chmod 644 {0};".format(auth_keys)
    )

    for command in commands:
        sudo(command)
