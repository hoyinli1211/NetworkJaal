FROM python:3.7-slim
COPY . /app
WORKDIR /app

RUN python -m venv /opt/venv

RUN ./opt/venv/bin/activate && pip install -r requirements.txt
EXPOSE 80

RUN mkdir ~/.streamlit
RUN cp config.toml ~/.streamlit/config.toml
RUN cp credentials.toml ~/.streamlit/credentials.toml
WORKDIR /app
ENTRYPOINT ["streamlit", "run"]
CMD . /opt/venv/bin/activate && exec python NetworkJaal.py
