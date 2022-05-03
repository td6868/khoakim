# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#
#############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from odoo.exceptions import UserError, ValidationError


class SaleOrderInvoicePayment(models.TransientModel):
    _name = "sale.order.invoice"

    advance_payment_method = fields.Selection([
        ('all', 'Thanh toán toàn bộ'),
        ('percentage', 'Đặt cọc theo tỷ lệ (%)'),
        ('fixed', 'Đặt cọc theo số tiền'),
    ], string='Chọn hình thức thanh toán?', default='all', required=True)
    count = fields.Integer()

    def _action_invoice_payment(self):
        id = self.env.context.get('active_ids')
        so = self.env['sale.order'].browse(id)
        inv = so.action_invoice_create(final=True)
        inv.action_post()