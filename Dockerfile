FROM python:3.12
ENV PYTHONUNBUFFERED 1
RUN mkdir /cyberpolygon
WORKDIR /cyberpolygon
ADD . /cyberpolygon/
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]