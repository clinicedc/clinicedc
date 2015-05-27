# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ExportHistory'
        db.create_table(u'export_exporthistory', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('user_created', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('user_modified', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('hostname_created', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('hostname_modified', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('app_label', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('object_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('export_uuid_list', self.gf('django.db.models.fields.TextField')(null=True)),
            ('pk_list', self.gf('django.db.models.fields.TextField')(null=True)),
            ('exit_message', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('exit_status', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('export_filename', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('export_file_contents', self.gf('django.db.models.fields.TextField')(null=True)),
            ('exported', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('exported_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('notification_plan_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sent_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('received', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('received_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('closed_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('edc_export', ['ExportHistory'])

        # Adding model 'ExportTransaction'
        db.create_table(u'export_exporttransaction', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('user_created', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('user_modified', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('hostname_created', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('hostname_modified', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('exported', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('exported_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('export_change_type', self.gf('django.db.models.fields.CharField')(default='I', max_length=1)),
            ('export_uuid', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
            ('tx', self.gf('django.db.models.fields.TextField')()),
            ('app_label', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('object_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('tx_pk', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('timestamp', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, db_index=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=15)),
            ('received', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('received_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('is_ignored', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_error', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('edc_export', ['ExportTransaction'])

        # Adding model 'ExportPlan'
        db.create_table(u'export_exportplan', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('user_created', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('user_modified', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('hostname_created', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('hostname_modified', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('app_label', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('object_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('fields', self.gf('django.db.models.fields.TextField')(max_length=500)),
            ('extra_fields', self.gf('django.db.models.fields.TextField')(max_length=500)),
            ('exclude', self.gf('django.db.models.fields.TextField')(max_length=500)),
            ('header', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('track_history', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('show_all_fields', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('delimiter', self.gf('django.db.models.fields.CharField')(default=',', max_length=1)),
            ('encrypt', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('strip', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('target_path', self.gf('django.db.models.fields.CharField')(default='~/edc_export', max_length=250)),
            ('notification_plan_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
        ))
        db.send_create_signal('edc_export', ['ExportPlan'])

        # Adding unique constraint on 'ExportPlan', fields ['app_label', 'object_name']
        db.create_unique(u'export_exportplan', ['app_label', 'object_name'])

        # Adding model 'ExportReceipt'
        db.create_table(u'export_exportreceipt', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('user_created', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('user_modified', self.gf('django.db.models.fields.CharField')(default='', max_length=250, db_index=True)),
            ('hostname_created', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('hostname_modified', self.gf('django.db.models.fields.CharField')(default='mac.local', max_length=50, db_index=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('export_uuid', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
            ('app_label', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('object_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('tx_pk', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('timestamp', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('received_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('edc_export', ['ExportReceipt'])


    def backwards(self, orm):
        # Removing unique constraint on 'ExportPlan', fields ['app_label', 'object_name']
        db.delete_unique(u'export_exportplan', ['app_label', 'object_name'])

        # Deleting model 'ExportHistory'
        db.delete_table(u'export_exporthistory')

        # Deleting model 'ExportTransaction'
        db.delete_table(u'export_exporttransaction')

        # Deleting model 'ExportPlan'
        db.delete_table(u'export_exportplan')

        # Deleting model 'ExportReceipt'
        db.delete_table(u'export_exportreceipt')


    models = {
        'edc_export.exporthistory': {
            'Meta': {'ordering': "('-sent_datetime',)", 'object_name': 'ExportHistory'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'closed_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'exit_message': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'exit_status': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'export_file_contents': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'export_filename': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'export_uuid_list': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'exported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exported_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'notification_plan_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'object_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'pk_list': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'received': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'received_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sent_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'user_created': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'})
        },
        'edc_export.exportplan': {
            'Meta': {'unique_together': "(('app_label', 'object_name'),)", 'object_name': 'ExportPlan'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'delimiter': ('django.db.models.fields.CharField', [], {'default': "','", 'max_length': '1'}),
            'encrypt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exclude': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            'extra_fields': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            'fields': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            'header': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'notification_plan_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'object_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'show_all_fields': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'strip': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'target_path': ('django.db.models.fields.CharField', [], {'default': "'~/edc_export'", 'max_length': '250'}),
            'track_history': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user_created': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'})
        },
        'edc_export.exportreceipt': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'ExportReceipt'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'export_uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'object_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'received_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'tx_pk': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'user_created': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'})
        },
        'edc_export.exporttransaction': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'ExportTransaction'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'export_change_type': ('django.db.models.fields.CharField', [], {'default': "'I'", 'max_length': '1'}),
            'export_uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'exported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exported_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'hostname_created': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'hostname_modified': ('django.db.models.fields.CharField', [], {'default': "'mac.local'", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'is_error': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_ignored': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'object_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'received': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'received_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '15'}),
            'timestamp': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'db_index': 'True'}),
            'tx': ('django.db.models.fields.TextField', [], {}),
            'tx_pk': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'user_created': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'}),
            'user_modified': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_index': 'True'})
        }
    }

    complete_apps = ['edc_export']