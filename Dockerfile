#FROM python:3.11-slim
FROM python:3.11
WORKDIR /app

RUN useradd -m bedrock && chown -R bedrock /app
USER bedrock
ENV PATH="/home/bedrock/.local/bin:${PATH}"

COPY --chown=bedrock:bedrock app.py chainlit.md .env /app/
COPY --chown=bedrock:bedrock requirements.txt /app/
COPY --chown=bedrock:bedrock public /app/public
RUN pip install --no-cache-dir -r requirements.txt

CMD ["chainlit", "run", "app.py", "-h"]
#CMD ["python", "-m", "chainlit", "run", "app.py", "-h", "--port", "8080"]