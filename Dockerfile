FROM centos:7
WORKDIR /doc-api
COPY . .
ENV FLASK_APP doc_api
ENV FLASK_RUN_PORT 7000
ENV FLASK_RUN_HOST 0.0.0.0
RUN yum install -y python3 poppler-utils zbar && \
    yum clean all
RUN pip3 install -e /doc-api/.
CMD ["flask", "run"]
