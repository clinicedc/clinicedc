Celery
======

Set up Celery workers and the Celery beat scheduler to run under systemd,
with one isolated service instance per environment (``live``, ``uat``,
``debug``).

See upstream docs:
https://docs.celeryq.dev/en/stable/userguide/daemonizing.html#usage-systemd

Sample unit files live in ``clinicedc/bin/systemd``:

- ``celery.live.service`` / ``celery.uat.service`` — workers
- ``celerybeat.service`` / ``celerybeat-uat.service`` — beat (scheduler)


Process isolation
+++++++++++++++++

Each environment runs under its **own** user and group so the UAT worker
cannot read, write to, or signal live processes (and vice versa).

- ``celery.live.service``     → ``User=live``  / ``Group=live``
- ``celery.uat.service``      → ``User=uat``   / ``Group=uat``
- ``celerybeat.service``      → ``User=live``  / ``Group=live``
- ``celerybeat-uat.service``  → ``User=uat``   / ``Group=uat``

Pid files, log files, and working directories must be owned by the same
user as the corresponding service, or the unit will fail to start.


Celery app module per environment
+++++++++++++++++++++++++++++++++

Create one celery app module per environment under your project's celery
folder, e.g. ``meta_edc.celery``:

.. code-block:: text

    meta_edc
        |--- celery
               |---debug.py
               |---live.py
               |---uat.py


Environment files
+++++++++++++++++

systemd reads environment variables from ``EnvironmentFile=``. Keep
**worker** and **beat** variables in separate files so the two services
can be restarted independently and the files can be owned/readable
separately if needed.

Worker env file — ``/etc/conf.d/celery.live.conf``:

.. code-block:: bash

    # Name of nodes to start
    CELERYD_NODES="w1 w2"

    # Absolute path to the 'celery' command inside the project venv
    CELERY_BIN="/home/live/edc/.venv/bin/celery"

    # App instance to use
    CELERY_APP="meta_edc.celery.live:app"

    # Extra command-line arguments to the worker
    CELERYD_OPTS="--time-limit=300 --concurrency=8"

    # - %n will be replaced with the first part of the nodename.
    # - %I will be replaced with the current child process index
    #   and is important when using the prefork pool to avoid race conditions.
    CELERYD_PID_FILE="/var/run/celery/%n.live.pid"
    CELERYD_LOG_FILE="/var/log/celery/%n%I.live.log"
    CELERYD_LOG_LEVEL="INFO"

.. note::

   ``CELERYD_USER``, ``CELERYD_GROUP``, and ``CELERYD_CHDIR`` are
   init-script conventions. Under systemd the equivalents are the
   ``User=``, ``Group=``, and ``WorkingDirectory=`` directives inside
   the ``.service`` file — do **not** set them in the environment file.

Beat env file — ``/etc/conf.d/celerybeat.live.conf``:

.. code-block:: bash

    CELERY_BIN="/home/live/edc/.venv/bin/celery"
    CELERY_APP="meta_edc.celery.live:app"

    CELERYBEAT_PID_FILE="/var/run/celery/celerybeat.live.pid"
    CELERYBEAT_LOG_FILE="/var/log/celery/celerybeat.live.log"
    CELERYD_LOG_LEVEL="INFO"

Repeat for UAT with ``uat`` substituted throughout
(``/etc/conf.d/celery.uat.conf``, ``/etc/conf.d/celerybeat.uat.conf``,
``CELERY_APP="meta_edc.celery.uat:app"``, etc.).


User accounts and file ownership
++++++++++++++++++++++++++++++++

Each environment has a dedicated system user that owns the venv, code
checkout, pid files, and log files for that environment:

.. code-block:: bash

    # pid + log directories
    sudo install -d -m 0755 -o live -g live /var/run/celery
    sudo install -d -m 0755 -o live -g live /var/log/celery

    # UAT gets its own paths or a shared directory that both users can
    # write into (prefer the former for stronger isolation):
    sudo install -d -m 0755 -o uat -g uat /var/run/celery-uat
    sudo install -d -m 0755 -o uat -g uat /var/log/celery-uat

Adjust the ``CELERYD_PID_FILE`` / ``CELERYD_LOG_FILE`` /
``CELERYBEAT_PID_FILE`` / ``CELERYBEAT_LOG_FILE`` paths in the env files
to match.

.. warning::

   Do **not** grant the ``celery`` user membership in the ``live`` or
   ``uat`` groups. Each environment runs as its own user; a shared
   ``celery`` account defeats the isolation described above.


Install Celery
++++++++++++++

Install into the project venv (as the environment's user):

.. code-block:: bash

    uv pip install -U "celery[redis]"

Or (non-uv hosts):

.. code-block:: bash

    pip install -U "celery[redis]"


Settings
++++++++

Enable Celery in settings or the project ``.env`` file:

.. code-block:: bash

    CELERY_ENABLED=True


Load and start services
+++++++++++++++++++++++

After copying the ``.service`` files from ``clinicedc/bin/systemd`` into
``/etc/systemd/system/`` (or symlinking them):

.. code-block:: bash

    sudo systemctl daemon-reload

    sudo systemctl enable celery.live.service celerybeat.service
    sudo systemctl enable celery.uat.service celerybeat-uat.service

    sudo systemctl start celery.live.service celerybeat.service
    sudo systemctl start celery.uat.service celerybeat-uat.service


Verify
++++++

.. code-block:: bash

    sudo systemctl status celery.live.service
    sudo systemctl status celery.uat.service
    sudo systemctl status celerybeat.service
    sudo systemctl status celerybeat-uat.service

Tail the logs:

.. code-block:: bash

    sudo journalctl -u celery.uat.service -f
    sudo tail -f /var/log/celery/w1.uat.log
    sudo tail -f /var/log/celery/celerybeat.uat.log


Restarting after a code deploy
++++++++++++++++++++++++++++++

After pulling new code or updating dependencies, restart the worker
(and beat, if periodic tasks changed):

.. code-block:: bash

    sudo systemctl restart celery.uat.service celerybeat-uat.service
    sudo systemctl restart celery.live.service celerybeat.service

All four units use ``Restart=always`` so systemd will bring them back up
if they crash. ``celerybeat*.service`` additionally sets ``RestartSec=5s``
to avoid a tight restart loop if beat is mis-configured.


Future: Django Tasks framework
++++++++++++++++++++++++++++++

Django 6.0 shipped the Tasks framework (DEP 14) but only with inline
(``immediate``) and ``dummy`` backends — no persistent backend in core.
Once a persistent/database backend ships in core Django (expected 7.x),
Celery in clinicedc will be replaced with Django Tasks and these systemd
units will be retired in favour of a ``manage.py`` worker command. No
action required until then.
