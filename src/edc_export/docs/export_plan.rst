Export Plans
=============

Edc Export uses export plans

For example::

    export_plan_setup = {
        'bcpp_subject.subjectreferral': {
            'app_label': 'bcpp_subject',
            'object_name': 'subjectreferral',
            'fields': [],
            'extra_fields': OrderedDict(
                {'plot_identifier': 'subject_visit__household_member__household_structure__household__plot__plot_identifier',
                 'dob': 'subject_visit__appointment__registered_subject__dob',
                 'first_name': 'subject_visit__appointment__registered_subject__first_name',
                 'identity': 'subject_visit__appointment__registered_subject__identity',
                 'identity_type': 'subject_visit__appointment__registered_subject__identity_type',
                 'initials': 'subject_visit__appointment__registered_subject__initials',
                 'last_name': 'subject_visit__appointment__registered_subject__last_name',
                 'subject_identifier': 'subject_visit__appointment__registered_subject__subject_identifier',
                 }),
            'exclude': [
                'comment',
                'created',
                'exported',
                'hostname_created',
                'hostname_modified',
                'in_clinic_flag',
                'modified',
                'referral_clinic_other',
                'revision',
                'subject_visit',
                'user_created',
                'user_modified',
                 ],
            'header': True,
            'track_history': True,
            'show_all_fields': True,
            'delimiter': '|',
            'encrypt': False,
            'strip': True,
            'target_path': '~/export_to_cdc',
            'notification_plan_name': 'referral_file_to_cdc',
        },
        'bcpp_subject.subjectlocator': {
            'app_label': 'bcpp_subject',
            'object_name': 'subjectlocator',
            'fields': [],
            'extra_fields': OrderedDict(
                {'plot_identifier': 'subject_visit__household_member__household_structure__household__plot__plot_identifier',
                 'dob': 'subject_visit__appointment__registered_subject__dob',
                 'first_name': 'subject_visit__appointment__registered_subject__first_name',
                 'identity': 'subject_visit__appointment__registered_subject__identity',
                 'identity_type': 'subject_visit__appointment__registered_subject__identity_type',
                 'initials': 'subject_visit__appointment__registered_subject__initials',
                 'last_name': 'subject_visit__appointment__registered_subject__last_name',
                 'subject_identifier': 'subject_visit__appointment__registered_subject__subject_identifier',
                 }),
            'exclude': [
                'exported',
                'created',
                'hostname_created',
                'hostname_modified',
                'modified',
                'revision',
                'subject_visit',
                'user_created',
                'user_modified',
                'registered_subject',
                 ],
            'header': True,
            'track_history': True,
            'show_all_fields': True,
            'delimiter': '|',
            'encrypt': False,
            'strip': True,
            'target_path': '~/export_to_cdc',
            'notification_plan_name': 'locator_file_to_cdc',
            }
        }

    notification_plan_setup = {
        'referral_file_to_cdc': {
            'name': 'referral_file_to_cdc',
            'friendly_name': 'BCPP Participant Referral File Transfer to Clinic',
            'subject_format': '{exit_status}: BCPP Referral File Transfer {timestamp}',
            'body_format': ('Dear BCPP File Transfer Monitoring Group Member,\n\nYou are receiving this email as a member '
                            'of the BCPP file transfer monitoring group. If you have any questions or comments regarding the contents '
                            'of this message please direct them to Erik van Widenfelt (ew2789@gmail.com).\n\n'
                            'To unsubscribe, please contact Erik van Widenfelt (ew2789@gmail.com).\n\n'
                            'File transfer status for {export_datetime} is as follows:\n\n'
                            '* Transfer Title: {notification_plan_name}\n'
                            '* Status: {exit_status}\n'
                            '* Status Message: {exit_status_message}\n'
                            '* Transaction count: {tx_count}\n'
                            '* File name: {file_name}\n\n'
                            'Thank You,\n\n'
                            'BHP Data Management Team\n'
                            ),
            'recipient_list': ['ew2789@gmail.com', 'bcpp_referral_monitoring@bhp.org.bw'],
            'cc_list': [],
            },
        'locator_file_to_cdc': {
            'name': 'locator_file_to_cdc',
            'friendly_name': 'BCPP Participant Locator File Transfer to Clinic',
            'subject_format': '{exit_status}: BCPP Locator File Transfer {timestamp}',
            'body_format': ('Dear BCPP File Transfer Monitoring Group Member,\n\nYou are receiving this email as a member '
                            'of the BCPP file transfer monitoring group. If you have any questions or comments regarding the contents '
                            'of this message please direct them to Erik van Widenfelt (ew2789@gmail.com).\n\n'
                            'To unsubscribe, please contact Erik van Widenfelt (ew2789@gmail.com).\n\n'
                            'File transfer status for {export_datetime} is as follows:\n\n'
                            '* Transfer Title: {notification_plan_name}\n'
                            '* Status: {exit_status}\n'
                            '* Status Message: {exit_status_message}\n'
                            '* Transaction count: {tx_count}\n'
                            '* File name: {file_name}\n\n'
                            'Thank You,\n\n'
                            'BHP Data Management Team\n'
                            ),
            'recipient_list': ['ew2789@gmail.com', 'bcpp_referral_monitoring@bhp.org.bw'],
            'cc_list': [],
            }
        }
 