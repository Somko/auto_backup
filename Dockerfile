FROM odoo:10

USER root

RUN apt update && apt install -y build-essential python-dev libssl-dev libffi-dev
RUN pip install workdays pygments packaging appdirs pysftp

USER odoo
