UV
==

Delpoy with uv
--------------

get uv

.. code-block:: bash

    curl -LsSf https://astral.sh/uv/install.sh | sh && \

log into you shell and ...

.. code-block:: bash

    mkdir ~/edc && \
    mkdir -p ~/.clinicedc/meta

add to your bashrc or zshrc

.. code-block::bash

    # >>> EDC using uv >>>
    export DJANGO_SETTINGS_MODULE=meta_edc.settings.uat
    export META_PHASE=3
    export DJANGO_BASE_DIR=/home/uat/edc/
    export DJANGO_ENV_DIR=/home/uat/.clinicedc/
    cd ~/edc
    source /home/uat/edc/.venv/bin/activate
    export PATH="/home/uat/edc:$PATH"
    # <<< EDC using uv <<<

build the venv and pip install meta-edc

.. code-block:: bash

    cd ~/edc && \
    uv venv --clear && \
    uv pip install -U meta-edc==1.1.10 && \
    wget -O manage.py https://raw.githubusercontent.com/meta-trial/meta-edc/1.1.10/manage.py && \
    uv pip freeze | grep meta-edc && \
    uv run --no-sources manage.py check

or build the venv within a cloned repo

.. code-block:: bash

    cd ~/edc && \
    git clone https://github.com/meta-trial/meta-edc.git && \
    git checkout main && \
    uv venv && \
    source .venv/bin/activate && \
    uv sync --no-sources && \
    uv run --no-sources manage.py check


if all is ok, migrate

.. code-block:: bash

    uv run --no-sources manage.py migrate --settings=meta_edc.settings.uat

now go to the systemd service files.

point gunicorn to the .venv folder in /etc/systemd/system/gunicorn-uat.service

.. code-block:: text

    [Unit]
    Description=gunicorn UAT daemon
    Requires=gunicorn-uat.socket
    After=network.target

    [Service]
    User=uat
    Group=www-data
    WorkingDirectory=/home/uat/edc
    Environment=DJANGO_SETTINGS_MODULE=meta_edc.settings.uat
    Environment=DJANGO_BASE_DIR=/home/uat/edc
    Environment=DJANGO_ENV_DIR=/home/uat/.clinicedc/
    ExecStart=/home/uat/edc/.venv/bin/gunicorn \
        --access-logfile - \
        --workers 2 \
        --timeout=300 \
        --bind unix:/run/gunicorn-uat.sock \
        meta_edc.wsgi_uat:application

    [Install]
    WantedBy=multi-user.target

restart gunicorn

.. code-block:: bash

    sudo systemctl restart gunicorn-uat



Run tests on the current releases
---------------------------------

.. code-block:: bash

    uv venv --clear && \
    source .venv/bin/activate && \
    uv run --active --group test --no-sources coverage run -a runtests.py && \
    uv run --active --group test coverage report

To run tests on locally cloned editable repos

.. code-block:: bash

    uv venv --clear && \
    source .venv/bin/activate && \
    uv run --active --group test coverage run -a runtests.py && \
    uv run --active --group test coverage report

commit

.. code-block:: bash

    rm uv.lock && \
    uv venv --clear && \
    source .venv/bin/activate && \
    uv sync --no-sources --no-dev && \
    uv tree
