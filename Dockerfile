FROM python:3.10-alpine

WORKDIR /app

COPY src/ /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "run_simulation.py"]

EXPOSE 5000