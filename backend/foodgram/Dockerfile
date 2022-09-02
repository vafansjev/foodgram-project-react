FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

# CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
RUN ["chmod", "+x", "/docker-entrypoint.sh"]
ENTRYPOINT [ "/bin/sh", "/docker-entrypoint.sh" ]
#CMD ./docker-entrypoint.sh