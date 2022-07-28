# FROM python:3.8.0
# WORKDIR /app
# COPY requirements.txt .
# COPY send_to_db.py .
# COPY .env .

# RUN apt-get update -y
# RUN apt-get update
# RUN apt-get install -y cmake
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt

# CMD ["python", "send_to_db.py"]

#########

FROM python:3.7
RUN mkdir /app
WORKDIR /app
#COPY pyproject.toml .
#COPY live_speed_limit_sensor/main.py .
#COPY .env .
#RUN apt-get update -y
#RUN apt-get install -y cmake
#RUN pip3 install --upgrade pip
#RUN pip install cython
#RUN pip install RUST
#RUN pip install cryptography
RUN pip3 install poetry
#RUN poetry install
RUN poetry -V

#CMD ["python", "main.py"]
