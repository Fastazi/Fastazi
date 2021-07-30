# Docker image for replication of Fastazi experiments
FROM ubuntu:20.04
ENV DIR=/home/fastazi
WORKDIR ${DIR}
# Allow package installation without extra prompt
ARG DEBIAN_FRONTEND=noninteractive
# Install required packages from apt-get
RUN apt-get update
                       # Required core packages
RUN apt-get install -y git curl wget unzip vim time subversion \
                       # Defects4J dependencies
                       perl libdbi-perl \
                       # Java version for the experiments
                       openjdk-8-jdk \
                       # Python/FAST dependencies
                       python python3 python3-pip
                       # Java build systems
RUN apt-get install -y ant maven
# Install PIP for necessary Python packages
# RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN pip3 install xxhash

# Clone Defects4J repository and perform setup
RUN git clone https://github.com/rjust/defects4j
RUN cpan --installdeps defects4j/
RUN /bin/bash /home/fastazi/defects4j/init.sh
ENV PATH "$PATH:/home/fastazi/defects4j/framework/bin"

CMD ["bash"]