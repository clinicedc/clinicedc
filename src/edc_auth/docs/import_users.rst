

To import users create a CSV of format:

.. code-block:: bash

	username,first_name,last_name,email,sites,groups,job_title
	pmetheny,Pat,Metheny,pmetheny@example.com,WITCHITA,"EVERYONE,ADMINISTRATION,CLINIC,PII,RANDO",Guitarist
	...
	...


Import the users from the CSV:

.. code-block:: python

	from edc_auth.import_users import import_users

	import_users(
		'/home/someuser/edc_witchita.csv',
		resource_name='witchita.sometrial.clinicedc.org',
		send_email_to_user=True,
		export_to_file=True,
		verbose=True)

The function will:

* import user into ``django.contrib.auth.models.User``;
* send an email informing the user that the account was created or updated.

If the user account already exists, the script will update the information without changing the username or password.

If ``export_to_file`` is ``True``, a new CSV file will be created in the same folder as the source file with columns:

.. code-block:: bash

	username,password,first_name,last_name,sites,groups
	pmetheny,reproach squeel dismount,Pat,Metheny,pmetheny@example.com,WITCHITA,"EVERYONE,ADMINISTRATION,CLINIC,PII,RANDO"
	...
	...

Passwords for existing accounts are not included in this new CSV file.
