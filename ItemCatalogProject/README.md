# Udacity Catalog Project (Project 2)

This is	a catalog app built with Python, Flask,	SQLAlchemy, HTML, & CSS.
This app incorporates user authentication & authorization using	Google
Authentication.	Users that are logged in have the ability to add categories and items
as well as delete & edit items. Users who are not logged in can	see categories and
items, but they	are not	allowed	to change anything.

## Set Up
1. Ensure git is installed. To install on Mac, install from: http://git-scm.com/download/mac. To install on Windows,
install from: http://git-scm.com/download/win
2. Ensure Python is installed. To install on Mac, install from:
https://www.python.org/ftp/python/2.7.12/python-2.7.12-macosx10.6.pkg
To install on Windows, install from: https://www.python.org/ftp/python/2.7.12/python-2.7.12.msi
3. Install Virtual Box from https://www.virtualbox.org/wiki/Downloads
4. Install Vagrant from https://www.vagrantup.com/downloads
5. Open command line
6. Change to the desired directory
7. Clone Udacity VM configuration with Git from	https://github.com/udacity/fullstack-nanodegree-vm.git
8. Move	to vagrant file
9. Download catalog project
10. Run	Vagrant	with command `vagrant up`
11. Login to VM	using command `vagrant ssh`
12. Move to Project2 directory /vagrant/Project2/
13. Set up the Python database by running the command `python database_setup.py`
14. Populate the database with command `python populate_database.py`
15. Run	the main project file with command `python project.py`
16. View the app in your browser by visiting http://localhost:5000/