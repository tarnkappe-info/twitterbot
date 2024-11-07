FROM python:3.9
RUN mkdir /pythondata
ADD twitterbot.py /pythondata/twitterbot.py
ADD requirements.txt /pythondata/requirements.txt
RUN pip install -r /pythondata/requirements.txt
