FROM python:3.8
RUN mkdir /opt/deadpool
WORKDIR /opt/deadpool
COPY . /opt/deadpool
CMD ["bin/bash"]