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

# Install Defects4J dependencies
RUN apt-get install -y perl libdbi-perl
# Clone Defects4J repository and perform setup
RUN git clone https://github.com/rjust/defects4j ../defects4j
RUN cpan --installdeps ../defects4j
RUN /bin/bash /home/defects4j/init.sh
ENV PATH "$PATH:/home/defects4j/framework/bin"

CMD ["bash"]

# https://cloud.r-project.org/src/base/R-3/R-3.6.3.tar.gz