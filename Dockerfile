# Docker image for replication of Fastazi experiments
FROM ubuntu:20.04
ENV DIR=/home/fastazi
WORKDIR ${DIR}
# Allow package installation without extra prompt
ARG DEBIAN_FRONTEND=noninteractive

# Required core packages
RUN apt-get update
RUN apt-get install -y git curl wget unzip vim time subversion
                       
# Java version for the experiments
RUN apt-get install -y openjdk-8-jdk
# Java build systems
RUN apt-get install -y ant maven

# Python
RUN apt-get install -y python python3 python3-pip
# Python packages
RUN pip3 install xxhash

# Install Rscript (as per https://cloud.r-project.org/)
RUN apt install -y --no-install-recommends software-properties-common dirmngr
RUN apt install -y libgeos-dev libudunits2-dev libgdal-dev libproj-dev
RUN wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
RUN add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"
RUN apt install -y --no-install-recommends r-base
# Rscript packages


# Install Defects4J dependencies
RUN apt-get install -y perl libdbi-perl
# Clone Defects4J repository and perform setup
RUN git clone https://github.com/rjust/defects4j
RUN cpan --installdeps defects4j/
RUN /bin/bash /home/fastazi/defects4j/init.sh
ENV PATH "$PATH:/home/fastazi/defects4j/framework/bin"

ENV PYTHONHASHSEED 0

CMD ["bash"]