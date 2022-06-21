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
    _name = "sale.order.invoice.kk"

    # advance_payment_method = fields.Selection([
    #     ('all', 'Thanh toán toàn bộ'),
    #     ('percentage', 'Đặt cọc theo tỷ lệ (%)'),
    #     ('fixed', 'Đặt cọc theo số tiền'),
    #     ('debt', 'Công nợ'),
    # ], string='Chọn hình thức thanh toán?', default='all', required=True)
    # amount = fields.Float(string="Số tiền thu được")
    # c_amount = fields.Float(string="Số tiền cọc", compute="compute_amount")
    # journal_id = fields.Many2one('account.journal', string="Sổ nhật ký", required=True)
    # partner_bank_id = fields.Many2one('res.partner.bank', string="Tài khoản nhận", required=True)
    # payment_date = fields.Date(string="Ngày thanh toán", default=fields.Date.context_today)
    # communication = fields.Char(string="Nội dung thanh toán")

    def _action_proccess_invoice_payment(self):
        id = self.env.context.get('active_ids')
        so = self.env['sale.order'].browse(id)
        if so.state not in ["sale", "done"]:
            so.action_confirm()
        inv = so._create_invoices()
        inv.action_post()
        return inv

    def action_inv_payment(self):
        iv = self._action_proccess_invoice_payment()
        return iv.action_register_payment()

    def action_debt_inv_payment(self):
        iv = self._action_proccess_invoice_payment()
        return {
                'warning': {
                                'title': ('Đã tạo hoá đơn'),
                                'message': ("Hãy kiểm tra hoá đơn %s, để tiến hành ghi nhận công nợ" % iv.name),
                            },
            }
