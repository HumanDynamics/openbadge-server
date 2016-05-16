# OpenBadge Django Server
================


## Installation
----------------

For a dev server, you need first to install [Virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) using Pip, [Autoenv](https://github.com/kennethreitz/autoenv) using Pip, and [MySQL](https://dev.mysql.com/doc/refman/5.6/en/osx-installation-pkg.html) using the preinstalled package or Homebrew. You also probably want to install [PyCharm Educational Edition](https://www.jetbrains.com/pycharm-educational/) if you don't have it (it's free for academic accounts!).

Once you have those, be sure to check out the code from this repository. CD into the base directory, and Autoenv should show a message about executing the .env file. Choose `yes`, since it has some very useful shortcuts we'll use.

Now, create a virtual environment:

    virtualenv env

With that created, you'll want to CD to a different directory and then back to the root project directory. This is to restart the Autoenv script with the environment you just created. Now, every time you CD into the base directory, it loads your virtual environment automatically.

First thing is to install the required libraries:

    In Ubuntu, first run: sudo apt-get install build-essential libssl-dev libffi-dev python-dev; pip install pycrypto
    pip install -r requirements.txt

You then will need to install MySQL Python, which isn't included in the requirements because the production server needs to not have it:

    In Ubuntu, first run: sudo apt-get install python-mysqldb libmysqlclient-dev
    pip install MySQL-python

From here on out you'll need to set up your MySQL database:

    fab -f deploy/fabric/deploy.py configure_local_db
    or, if you have a root passwod set for mySQL, fab -f deploy/fabric/deploy.py configure_local_db:root_password=YOU_PASSWORD

With that in place, you can now set up the database tables. You can use the shortcut provided in .env:

    sudo mkdir /var/log/django
    sudo chmod 777 -R  /var/log/django
    migrate

You'll also want to create your super user. There's currently no shortcut for this:

    python src/manage.py createsuperuser --settings=project.localsettings

That should be it! At this point, all you need to do is run the server, then log into your admin to put data into it.

    runserver


## Deployment
----------------

In order to deploy the server to production, you need four files that are not checked in. Get `github_rsa`, `github_rsa.pub`, `sshkey`, and `sshkey.pub` from someone via email, and put them in the directory `deploy/fabric/keys`.

At that point all you need to deploy the code to production is to run the command:

    fab -f deploy/fabric/deploy.py -H {HOSTNAME} deploy


## Production Server Setup
----------------

If the repository is public, you will not need to create a Github access token. Otherwise, if it is private, follow [the instructions here](https://help.github.com/articles/creating-an-access-token-for-command-line-use/) to get a Personal Access Key.

If the project has already been set up with SSH keys, be sure to get them from someone. Just put the keys in the deploy/fabric/keys/ directory. If you don't have any keys there, they will be created automatically when you create a deploy user.

Ensure you have a `passwords.py` file located on the root of this project's directory, and that it has the proper usernames and passwords in it. It should have the exact variables and format of `src/project/passwords.py.template`, only the passwords and usernames should be filled in.


Now that we have the correct files, create a deploy user on your server:

    fab -f deploy/fabric/create_deploy_user.py -H {{ YOUR USERNAME HERE }}@{{ YOUR HOSTNAME HERE }} create
    
Or, if you are using an SSHConfig HostName alias, just use this:

    fab -f deploy/fabric/create_deploy_user.py -H {{ HOSTNAME }} create

To make sure it worked, run this command to test that the user was created:

    fab -f deploy/fabric/deploy.py -H {{ YOUR HOSTNAME HERE }} test

Then just run the command:

    fab -f deploy/fabric/deploy.py -H {{ YOUR HOSTNAME HERE }} setup_server

This command is safe to run on a server that's already been set up, though you should avoid it if possible.

After that, you just need to configure Django.

    fab -f deploy/fabric/deploy.py -H {{ YOUR HOSTNAME HERE }} create_superuser
    
Now you're all set and you should be able to log in to your admin console on your server!


## Notes
---------------

If you use autoenv, there are many shortcut aliases included to make your life simpler. They change too often to put them in the README, but check out the .env file to see what they are.
