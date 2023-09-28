
# Habit Tracker Project

A Project For Habit Tracking where user track their Habits on daily basis/weekly basis.

# Project Stack:
Python >= 3.9
Django FrameWork
Html
Bootstrap5
DbSqlite



## Installation 

Install venv for the project

```bash
  python -m venv venv
  # window user
  source venv/scripts/activate
  # linux
  source venv/bin/activate
  # After Activation
  go to project folder
  # install dependencies packages
  pip install -r requirements.txt
 
  # run server command 
  # use folder database, data is already populated in this.  login with username:admin pwd:admin
  # weekly/daily habits are linked with the user.
  python manage.py runserver
  # http://127.0.0.1:8000
  
  # Login Url
  http://127.0.0.1:8000/accounts/login/
  # SignUp Url
  http://127.0.0.1:8000/accounts/signup/
  
  # Run unit tests command
  python manage.py test 
 
 

```
## Useful Commands Of Django
``` bash
python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser
admin credentials:
email: admin@gmail.com
pwd : admin
```
