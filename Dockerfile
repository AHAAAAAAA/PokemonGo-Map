FROM python:2-alpine

# Install dependencies
RUN apk --update add --virtual build-deps openssl ca-certificates python-dev build-base gcc

# Copy and install requirements.txt only to minimize image rebuilding on updates
COPY requirements.txt /myapp/requirements.txt
WORKDIR /myapp
RUN pip install --no-cache-dir -r requirements.txt

# Remove unneeded caches
RUN apk del build-deps
RUN rm -rf /var/cache/apk/*

# Copy in the full application
COPY . /myapp

CMD ["python", "runserver.py", "-h"]
