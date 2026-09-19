# JARVIS Autonomous Agent — No Manual Intervention
FROM python:3.12-slim
WORKDIR /opt/jarvis
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV JARVIS_MODE=autonomous
ENV STARK_PROTOCOL=active
EXPOSE 8000
CMD ["python", "main.py", "--autonomous"]
