echo "Rest migrations and drop/create DB? Cannot be undone! (Hit CTRL-C to cancel)"
mysql -u root -p -Bse 'drop database edc_pharmacy; create database edc_pharmacy character set utf8;'
rm -rf edc_pharmacy/migrations/
# rm db.sqlite3
# mysql -u root -p -Bse 'create database edc_pharmacy character set utf8;'
python manage.py makemigrations edc_pharmacy
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

