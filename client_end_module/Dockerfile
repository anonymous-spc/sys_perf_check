FROM python:3.8
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY run_instructions.py .
EXPOSE 5500
CMD ["python3", "run_instructions.py"]