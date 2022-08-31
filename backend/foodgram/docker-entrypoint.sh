echo "Apply database migrations"
python manage.py migrate --noinput
echo "Collect static files"
python manage.py collectstatic --no-input
echo "Starting gunicorn server"
gunicorn foodgram.wsgi:application --bind 0:8000