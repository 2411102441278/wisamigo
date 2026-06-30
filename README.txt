   python -m venv venv
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   http://127.0.0.1:8000/

   python manage.py createsuperuser
   http://127.0.0.1:8000/admin/

DATA YANG DISIMPAN:
- Register/Login akun       = auth_user
- Edit Profile              = travel_userprofile
- Data destinasi            = travel_destination
- Data hotel / room         = travel_room
- Data booking / reservasi  = travel_booking
- Data review               = travel_review
- Data help artikel         = travel_helparticle
