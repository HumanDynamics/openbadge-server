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

    pip install -r requirements.txt

You then will need to install MySQL Python, which isn't included in the requirements because the production server needs to not have it:

    pip install MySQL-python

From here on out you'll need to set up your MySQL database:

    fab -f deploy/fabric/deploy.py configure_local_db

With that in place, you can now set up the database tables. You can use the shortcut provided in .env:

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

Like Deployment, you'll need the four SSH keys before you can do this. To configure a production server, first set up the user we user to SSH in from here on out:

    fab -f deploy/fabric/create_deploy_user.py -H {{ YOUR USERNAME HERE }}@{{ YOUR HOSTNAME HERE }} create

Then just run the command:

    fab -f deploy/fabric/deploy.py -H {{ YOUR HOSTNAME HERE }} setup_server

This command is safe to run on a server that's already been set up, though you should avoid it if possible.


## Notes
---------------

TBD
