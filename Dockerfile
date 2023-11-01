FROM python:3.10-alpine3.17

COPY bot_v01.py db_action.py messenger_v01.py requests_rates.py requirements.txt service.py /bot/

RUN pip3 install -r /bot/requirements.txt

CMD [ "python", "/bot/bot_v01.py" ]