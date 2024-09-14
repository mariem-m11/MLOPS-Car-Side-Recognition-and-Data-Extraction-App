FROM debian:stable

WORKDIR /app

RUN apt-get update && apt-get install -y python3-pip python3-venv

RUN python3 -m venv /app/venv

# Activate the virtual environment
ENV PATH="/app/venv/bin:$PATH"

RUN apt-get update --fix-missing && apt-get -y install tesseract-ocr && pip install pytesseract

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["uvicorn", "appfast:app", "--host", "0.0.0.0", "--port", "8080"]
