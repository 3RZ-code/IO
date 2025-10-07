FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY  . /app/

CMD ["python", "mange.py", "runserver", "0.0.0.0:8000"]
