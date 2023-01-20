FROM python:3.10-slim

ARG TESTING=0

# make sure it doesnt fail if the docker file doesnt know the git commit
ARG GIT_PYTHON_REFRESH=quiet

# copy files
COPY ./setup.py app/setup.py
COPY requirements.txt app/requirements.txt

# install requirements
RUN pip install -r app/requirements.txt

# copy library files
COPY ./pvsite_datamodel/ app/pvsite_datamodel/
COPY tests/ app/tests/

# change to app folder
WORKDIR /app

# install library
RUN pip install -e .

RUN if [ "$TESTING" = 1 ]; then pip install pytest pytest-cov coverage; fi

