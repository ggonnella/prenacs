# syntax=docker/dockerfile:1
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND noninteractive

#
# install Python and some base tools
#
USER root
RUN apt-get update -y
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get install -y python3.8 python3-pip wget curl git time
RUN ln -s /usr/bin/python3.8 /usr/bin/python
#
# install MariaDB and Python connector
#
ENV MARIADB_ROOT_PASSWORD=$MARIADB_ROOT_PASSWORD
ENV MARIADB_PASSWORD=$MARIADB_PASSWORD
ENV MARIADB_USER=$MARIADB_USER
RUN wget https://downloads.mariadb.com/MariaDB/mariadb_repo_setup
RUN chmod +x mariadb_repo_setup
RUN ./mariadb_repo_setup --mariadb-server-version=mariadb-10.6
RUN apt-get install -y mariadb-server libmariadb3 libmariadb-dev
RUN pip install mariadb
#
# install prenacs and ntmirror
#
ADD . /prenacs/
RUN cd /prenacs && pip install -e .
RUN cd /prenacs/attrtables && pip install -e .
RUN cd /prenacs/multiplug && pip install -e .
RUN cd /prenacs/snacli && pip install -e .
EXPOSE 8050
#
# install packages for testing
#
RUN pip install pytest pytest-console-scripts pytest-cov
COPY docker/config.yaml /prenacs/tests/config.yaml

# start MariaDB server

ENV PATH=$PATH:/prenacs/docker
WORKDIR /prenacs/
CMD ["mariadbd-safe"]
ENTRYPOINT [ "/bin/bash", "-l", "-c" ]
