FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["./install.sh"]
CMD ["uvicorn", "app.my_REST_api:app", "--host", "0.0.0.0", "--port", "80"]