# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RegisteredSubjectAudit'
        db.create_table('bhp_registration_registeredsubject_audit', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('user_created', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('user_modified', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('hostname_created', self.gf('django.db.models.fields.CharField')(default='mac2-2.local', max_length=50)),
            ('hostname_modified', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('_audit_subject_identifier', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('subject_identifier_as_pk', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, db_index=True)),
            ('subject_identifier_aka', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('dm_comment', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=78L, null=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=78L, null=True)),
            ('initials', self.gf('django.db.models.fields.CharField')(max_length=78L, null=True)),
            ('dob', self.gf('django.db.models.fields.DateField')(null=True)),
            ('is_dob_estimated', self.gf('django.db.models.fields.CharField')(max_length=25, null=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('subject_type', self.gf('django.db.models.fields.CharField')(max_length=25, null=True)),
            ('subject_identifier', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, blank=True)),
            ('subject_consent_id', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('registration_identifier', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('sid', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('study_site', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='_audit_registeredsubject', null=True, to=orm['bhp_variables.StudySite'])),
            ('relative_identifier', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('identity', self.gf('django.db.models.fields.CharField')(max_length=78L, null=True, blank=True)),
            ('identity_type', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('may_store_samples', self.gf('django.db.models.fields.CharField')(default='?', max_length=3)),
            ('hiv_status', self.gf('django.db.models.fields.CharField')(max_length=15, null=True)),
            ('survival_status', self.gf('django.db.models.fields.CharField')(max_length=15, null=True)),
            ('screening_identifier', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('screening_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('screening_age_in_years', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('registration_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('randomization_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('registration_status', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(max_length=250, null=True, blank=True)),
            ('additional_key', self.gf('django.db.models.fields.CharField')(default=None, max_length=36, null=True)),
            ('salt', self.gf('django.db.models.fields.CharField')(default='salt', max_length=25, null=True)),
            ('_audit_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('_audit_change_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('_audit_id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
        ))
        db.send_create_signal('registration', ['RegisteredSubjectAudit'])

        # Adding model 'RegisteredSubject'
        db.create_table('bhp_registration_registeredsubject', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('user_created', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('user_modified', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('hostname_created', self.gf('django.db.models.fields.CharField')(default='mac2-2.local', max_length=50)),
            ('hostname_modified', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=75, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('subject_identifier_as_pk', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, db_index=True)),
            ('subject_identifier_aka', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('dm_comment', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=78L, null=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=78L, null=True)),
            ('initials', self.gf('django.db.models.fields.CharField')(max_length=78L, null=True)),
            ('dob', self.gf('django.db.models.fields.DateField')(null=True)),
            ('is_dob_estimated', self.gf('django.db.models.fields.CharField')(max_length=25, null=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('subject_type', self.gf('django.db.models.fields.CharField')(max_length=25, null=True)),
            ('subject_identifier', self.gf('django.db.models.fields.CharField')(db_index=True, unique=True, max_length=50, blank=True)),
            ('subject_consent_id', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('registration_identifier', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
            ('sid', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('study_site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bhp_variables.StudySite'], null=True, blank=True)),
            ('relative_identifier', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('identity', self.gf('django.db.models.fields.CharField')(max_length=78L, null=True, blank=True)),
            ('identity_type', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('may_store_samples', self.gf('django.db.models.fields.CharField')(default='?', max_length=3)),
            ('hiv_status', self.gf('django.db.models.fields.CharField')(max_length=15, null=True)),
            ('survival_status', self.gf('django.db.models.fields.CharField')(max_length=15, null=True)),
            ('screening_identifier', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, blank=True)),
#             ('screening_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
#             ('screening_age_in_years', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('registration_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('randomization_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('registration_status', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(max_length=250, null=True, blank=True)),
            ('additional_key', self.gf('django.db.models.fields.CharField')(default=None, max_length=36, null=True)),
            ('salt', self.gf('django.db.models.fields.CharField')(default='salt', max_length=25, null=True)),
        ))
        db.send_create_signal('registration', ['RegisteredSubject'])

        # Adding unique constraint on 'RegisteredSubject', fields ['first_name', 'dob', 'initials', 'additional_key']
        db.create_unique('bhp_registration_registeredsubject', ['first_name', 'dob', 'initials', 'additional_key'])


    def backwards(self, orm):
        # Removing unique constraint on 'RegisteredSubject', fields ['first_name', 'dob', 'initials', 'additional_key']
        db.delete_unique('bhp_registration_registeredsubject', ['first_name', 'dob', 'initials', 'additional_key'])

        # Deleting model 'RegisteredSubjectAudit'
        db.delete_table('bhp_registration_registeredsubject_audit')

        # Deleting model 'RegisteredSubject'
        db.delete_table('bhp_registration_registeredsubject')


    models = {
        'bhp_variables.studysite': {
            'Meta': {'ordering': "['site_code']", 'unique_together': "[('site_code', 'site_name')]", 'object_name': 'StudySite'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac2-2.local'", 'max_length': '50'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'site_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '4'}),
            'site_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '35'}),
            'user_created': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'registration.registeredsubject': {
            'Meta': {'ordering': "['subject_identifier']", 'unique_together': "(('first_name', 'dob', 'initials', 'additional_key'),)", 'object_name': 'RegisteredSubject', 'db_table': "'bhp_registration_registeredsubject'"},
            'additional_key': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '36', 'null': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'dm_comment': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '78L', 'null': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'hiv_status': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac2-2.local'", 'max_length': '50'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '78L', 'null': 'True', 'blank': 'True'}),
            'identity_type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'initials': ('django.db.models.fields.CharField', [], {'max_length': '78L', 'null': 'True'}),
            'is_dob_estimated': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '78L', 'null': 'True'}),
            'may_store_samples': ('django.db.models.fields.CharField', [], {'default': "'?'", 'max_length': '3'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'randomization_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'registration_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'registration_identifier': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'registration_status': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'relative_identifier': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'salt': ('django.db.models.fields.CharField', [], {'default': "'salt'", 'max_length': '25', 'null': 'True'}),
#             'screening_age_in_years': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
#             'screening_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'screening_identifier': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'study_site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bhp_variables.StudySite']", 'null': 'True', 'blank': 'True'}),
            'subject_consent_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'subject_identifier': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '50', 'blank': 'True'}),
            'subject_identifier_aka': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'subject_identifier_as_pk': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'db_index': 'True'}),
            'subject_type': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True'}),
            'survival_status': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            'user_created': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'registration.registeredsubjectaudit': {
            'Meta': {'ordering': "['-_audit_timestamp']", 'object_name': 'RegisteredSubjectAudit', 'db_table': "'bhp_registration_registeredsubject_audit'"},
            '_audit_change_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            '_audit_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            '_audit_subject_identifier': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            '_audit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'additional_key': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '36', 'null': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'dm_comment': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '78L', 'null': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'hiv_status': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac2-2.local'", 'max_length': '50'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '78L', 'null': 'True', 'blank': 'True'}),
            'identity_type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'initials': ('django.db.models.fields.CharField', [], {'max_length': '78L', 'null': 'True'}),
            'is_dob_estimated': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '78L', 'null': 'True'}),
            'may_store_samples': ('django.db.models.fields.CharField', [], {'default': "'?'", 'max_length': '3'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'randomization_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'registration_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'registration_identifier': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'registration_status': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'relative_identifier': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'salt': ('django.db.models.fields.CharField', [], {'default': "'salt'", 'max_length': '25', 'null': 'True'}),
#             'screening_age_in_years': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
#             'screening_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'screening_identifier': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'study_site': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_audit_registeredsubject'", 'null': 'True', 'to': "orm['bhp_variables.StudySite']"}),
            'subject_consent_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'subject_identifier': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'subject_identifier_aka': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'subject_identifier_as_pk': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'db_index': 'True'}),
            'subject_type': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True'}),
            'survival_status': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            'user_created': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['registration']