FROM python:2.7-alpine

RUN apk update && apk add build-base ca-certificates curl git libffi-dev openssl-dev wget

RUN wget -q https://releases.hashicorp.com/packer/1.3.3/packer_1.3.3_linux_amd64.zip && \
	test `sha256sum ./packer_1.3.3_linux_amd64.zip | cut -f1 -d' '` == `curl -v --silent https://releases.hashicorp.com/packer/1.3.3/packer_1.3.3_SHA256SUMS 2>&1 | grep packer_1.3.3_linux_amd64.zip | cut -f1 -d' '` && \
  	unzip ./packer_1.3.3_linux_amd64.zip -d /usr/bin
RUN wget -q https://releases.hashicorp.com/terraform/0.11.11/terraform_0.11.11_linux_amd64.zip && \
	test `sha256sum ./terraform_0.11.11_linux_amd64.zip | cut -f1 -d' '` == `curl -v --silent https://releases.hashicorp.com/terraform/0.11.11/terraform_0.11.11_SHA256SUMS 2>&1 | grep terraform_0.11.11_linux_amd64.zip | cut -f1 -d' '` && \
        unzip ./terraform_0.11.11_linux_amd64.zip -d /usr/bin

RUN mkdir -p /opt/heptio/wardroom
COPY . /opt/heptio/wardroom/
COPY .git /opt/heptio/wardroom/
WORKDIR /opt/heptio/wardroom
RUN pip install -r requirements.txt
RUN python setup.py install
