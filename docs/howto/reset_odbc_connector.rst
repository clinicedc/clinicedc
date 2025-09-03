Reset ODBC Connection
=====================

Sometimes Windows loses the ODBC connection in STATA

To rectify, try removing and re-adding the ODBC configuration like this:

1. Close STATA

2. Start the ssh tunnel / connection (`start_ssh_tunnel.bat`) and login

3. Open the ODBC Data Source Administrator

.. code-block:: text

    Start > Run > ODBC Data Source Administrator (64-bit)
    User DSN  > Add
    Select: MySQL 9.x Unicode Driver
    Configure as follows:
    Data Source Name: effect_production
    TCP/IP Server:   127.0.0.1
    Port: 3306
    User: <username>
    Password: <password>
    Database: effect_production
    Click Test, and it should be successful

4. Re-open STATA, type `odbc list` and you should see the (new) connection
