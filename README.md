# System Requirements
1. OS - Ubuntu Server 18.04 LTS (HVM)
2. SSD - 8GB
3. AWS Insance Type - t2.micro

# Pre Requisite Installation Steps
1. Repository Setup
   1. $ mkdir -p ~/workspace && cd ~/workspace
   2. $ git clone https://github.com/vikas91/black-jack.git
2. Python3, Pip, virtualenv Setup
   1. Ubuntu 18 comes with python3 installed. If not follow the link [here](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)
   2. $ sudo apt install pip3
   3. $ sudo pip3 install virtuale
   
# Project Setup instructions
1. $ cd ~/workspace/black-jack
2. $ virtualenv packages
3. $ source packages/bin/activate
4. $ pip install -r requirements.txt
5. $ cd ~/workspace/black-jack/webapp
6. $ python manage.py makemigrations webapp
7. $ python manage.py migrate

# Django Server Running Instructions
8. $ screen 
9. $ python manage.py runserver 0.0.0.0:8000
10.$ ctrl + a + d (detach from screen)

# Superuser Creation
1. $ cd ~/workspace/black-jack/webapp
2. $ python manage.py createsuperuser
3. Create tables by adding minimum bet value for the table by visiting admin url http://0.0.0.0:8000



