# Arif Menu (Version 1)
Free menu pages + QR codes + dish search. Django 5.

## Run
    python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py makemigrations core   # if you already ran an older version, this adds the new "type" field
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver
Open http://127.0.0.1:8000 and admin at /admin/.

## Flow
1. Owner signs up, picks a type (café, hotel...), adds place + menu items (text, optional photos).
2. You open /admin/ -> Places, tick **Is active** to approve, **Is featured** for the front page, set **Plan** to premium after payment.
3. Customers search dishes/places/area/price at the home page. Each place has a QR at /p/<slug>/qr.svg.

## Before going live
Set env vars: DEBUG=0, SECRET_KEY=<long random>, ALLOWED_HOSTS=yourdomain.com. Use PostgreSQL and cloud image storage; serve media properly.
