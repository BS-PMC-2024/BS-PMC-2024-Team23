FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
COPY Templates ./

EXPOSE 5000

CMD ["python", "main.py"]
