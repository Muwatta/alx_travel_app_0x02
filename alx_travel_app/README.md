# ALX Travel App

This Django project simulates a simple travel booking system with integrated payment handling.

## Features
- Create and manage travel bookings  
- Record and track payments  
- Uses Django ORM and SQLite  
- Ready for Chapa API integration  

## Setup
```bash
git clone <your-repo-url>
cd alx_travel_app_0x02
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
