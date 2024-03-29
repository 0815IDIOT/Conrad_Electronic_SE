FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code

RUN /code/install.sh

CMD ["uvicorn", "recommendation_api:app", "--host", "0.0.0.0", "--port", "80"]
