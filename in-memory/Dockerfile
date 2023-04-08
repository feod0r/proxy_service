FROM python:3.10

WORKDIR /code

COPY requirements.txt .
COPY proxy_list.json .

RUN pip install -r requirements.txt

COPY app.py .

CMD [ "python", "./app.py" ]
