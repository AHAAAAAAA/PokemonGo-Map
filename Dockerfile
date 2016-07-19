FROM python:2.7

ARG base_dir=/opt/pokemongo-map
WORKDIR ${base_dir}
EXPOSE 80
RUN apt-get update && apt-get install -y python-dev

COPY requirements.txt ${base_dir}/requirements.txt
RUN pip install -r ${base_dir}/requirements.txt

COPY . ${base_dir}

ENTRYPOINT ["python", "example.py"]

# CMD ["-H 0.0.0.0", "-P 80"]