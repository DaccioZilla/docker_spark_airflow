FROM apache/airflow:2.6.3

USER root

# Install Java
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk-headless wget build-essential libncursesw5-dev libssl-dev \
     libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz && \
    tar xzf Python-3.10.13.tgz  && \
    cd Python-3.10.13 && \
    ./configure --enable-optimizations && \
    make install  

# Download Spark
ENV SPARK_VERSION=3.3.3
ENV HADOOP_VERSION=3.3.2
ENV SPARK_HOME /usr/local/spark

## instalação do spark
RUN cd "/tmp" && \
        wget --no-verbose "https://archive.apache.org/dist/spark/spark-3.3.3/spark-3.3.3-bin-hadoop3.tgz" && \
        tar -xzf "spark-3.3.3-bin-hadoop3.tgz" && \
        mkdir -p "${SPARK_HOME}/bin" && \
        mkdir -p "${SPARK_HOME}/jars" && \
        mkdir -p "${SPARK_HOME}/conf" && \
        cp -a "spark-3.3.3-bin-hadoop3/bin/." "${SPARK_HOME}/bin" && \
        cp -a "spark-3.3.3-bin-hadoop3/jars/." "${SPARK_HOME}/jars" && \
        rm "spark-3.3.3-bin-hadoop3.tgz"

RUN export SPARK_HOME
ENV PATH $PATH:$SPARK_HOME/bin

## instalação dos jars para o minIO
RUN curl -O https://repo1.maven.org/maven2/software/amazon/awssdk/s3/2.18.41/s3-2.18.41.jar \
    && curl -O https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk/1.12.367/aws-java-sdk-1.12.367.jar \
    && curl -O https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.1026/aws-java-sdk-bundle-1.11.1026.jar \
    && curl -O https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.2.0/delta-core_2.12-2.2.0.jar \
    && curl -O https://repo1.maven.org/maven2/io/delta/delta-storage/2.2.0/delta-storage-2.2.0.jar \
    && curl -O https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.2/hadoop-aws-3.3.2.jar\
    && mv s3-2.18.41.jar $SPARK_HOME/jars \
    && mv aws-java-sdk-1.12.367.jar $SPARK_HOME/jars \
    && mv aws-java-sdk-bundle-1.11.1026.jar $SPARK_HOME/jars \
    && mv delta-core_2.12-2.2.0.jar $SPARK_HOME/jars \
    && mv hadoop-aws-3.3.2.jar $SPARK_HOME/jars \
    && mv delta-storage-2.2.0.jar $SPARK_HOME/jars



# Install only spark-submit
RUN ln -s $SPARK_HOME/bin/spark-submit /usr/local/bin/spark-submit

USER airflow
COPY requirements.txt .
RUN pip install -r requirements.txt
