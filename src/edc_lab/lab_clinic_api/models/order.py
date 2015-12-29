import logging

from django.core.urlresolvers import reverse
from django.db import models

from lis.exim.lab_import_dmis.classes.dmis_tools import DmisTools
from lis.specimen.lab_order.models import BaseOrder

from ..managers import OrderManager

from .aliquot import Aliquot
from .aliquot_condition import AliquotCondition
from .panel import Panel


logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class Order(BaseOrder):
    """Stores orders and is in a one to many relation with :class:`Aliquot` where one aliquot may
    have multiple orders and in a one-to-many relation with :class:`Result` where one order
    should only have one final result (but not enforced by the DB)."""

    aliquot = models.ForeignKey(Aliquot)

    panel = models.ForeignKey(Panel)

    subject_identifier = models.CharField(
        max_length=50,
        null=True,
        editable=False,
        db_index=True,
        help_text="non-user helper field to simplify search and filtering")

    receive_identifier = models.CharField(
        max_length=25, editable=False, null=True, db_index=True,
        help_text="non-user helper field to simplify search and filter")

    objects = OrderManager()

    def natural_key(self):
        return self.order_identifier

    def save(self, *args, **kwargs):

        self.subject_identifier = self.aliquot.receive.registered_subject.subject_identifier
        self.receive_identifier = self.aliquot.receive_identifier
        super(Order, self).save(*args, **kwargs)

    def get_status(self):
        """Gets the status of this order based on a few conditions.

            * COMPLETE: either the result items exist or it is a storage panel
            * PENDING: no results
            * ERROR: has results but condition is not OK
            * REDRAW: no results, condition not OK
            * WITHDRAWN: no results AND no longer exists on LIS

        .. todo:: a PARTIAL status is not yet handled.
        """

        # update status
        # TODO: this needs to consider "partial" status based on the testcodes that are defined
        # in the panel.
        # get the condition OK aliquot condition instance
        result_item_cls = models.get_model(self._meta.app_label, 'resultitem')
        aliquot_condition_ok = AliquotCondition.objects.get_ok()
        if not self.aliquot.aliquot_condition:
            # how can this be ??
            status = 'ERROR'
        elif result_item_cls.objects.filter(result__order=self) or self.panel.panel_type == 'STORAGE':
            # test aliquot condition and set the order status
            if self.aliquot.aliquot_condition == aliquot_condition_ok:
                status = 'COMPLETE'
            else:
                # has results or is stored but condition is not 10
                # was this meant to be a storage panel?
                status = 'ERROR'
        elif self.aliquot.aliquot_condition != aliquot_condition_ok:
            status = 'REDRAW'
        else:
            status = 'PENDING'
        # regardless of status, check that order was not deleted on DMIS
        dmis_tools = DmisTools()
        if dmis_tools.is_withdrawn_order(self):
            # other aspects of result visibility must consider this value
            status = 'WITHDRAWN'
        return status

    def get_status_message(self):
        if self.status == 'WITHDRAWN':
            msg = 'Warning: this order has been flagged as WITHDRAWN. The result is not valid.'
        elif self.status == 'DUPLICATE':
            msg = 'Warning: this order has been flagged as DUPLICATE. Please resolve.'
        else:
            msg = None
        return msg

    def to_receive(self):
        return '<a href="/admin/lab_clinic_api/receive/?q={receive_identifier}">receive</a>'.format(receive_identifier=self.aliquot.receive.receive_identifier)
    to_receive.allow_tags = True

    def to_result(self):
        if self.status.lower() in ('complete', 'error', 'duplicate'):
            return '<a href="/admin/lab_clinic_api/result/?q={order_identifier}">result</a>'.format(order_identifier=self.order_identifier)
        else:
            return ''
    to_result.allow_tags = True

    def get_absolute_url(self):
        return reverse('admin:lab_clinic_api_order_change', args=(self.id,))

    def __unicode__(self):
        return '%s' % (self.order_identifier)

    class Meta:
        app_label = 'lab_clinic_api'
        ordering = ['order_identifier']
