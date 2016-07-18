FROM python:2.7-onbuild
EXPOSE 5000
ENTRYPOINT ["python", "./runserver.py"]

