FROM odoo:10

USER root

RUN apt update && apt install -y build-essential python-dev libssl-dev libffi-dev
RUN pip install pygments packaging appdirs pysftp pysmb

USER odoo
