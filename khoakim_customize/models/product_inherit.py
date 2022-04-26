# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class SaleOrderLinesCustomize(models.Model):
    _inherit = 'sale.order.line'

    prod_image = fields.Binary(string="Ảnh sản phẩm", related="product_id.image_1920")
    qty_available = fields.Float(string="Tồn kho", related="product_id.qty_available")

class ProductProductCustomize(models.Model):
    _inherit = 'product.product'

    @api.onchange('default_code')
    def action_duplicate_code(self):
        if self.default_code:
            dup_code = self.env['product.product'].search([('default_code', '=', self.default_code)])
            if dup_code:
                code = self.default_code
                self.default_code = False
                return {
                    'warning': {'title': ('Trùng sản phẩm'), 'message': (
                                ("Mã %s đã bị trùng với sản phẩm %s, vui lòng chọn mã khác") % (code, dup_code))},
                }

class ResPartnerCustomize(models.Model):
    _inherit = 'res.partner'

    phone = fields.Char(string="Số điện thoại", required=True)

    @api.onchange('phone')
    def action_duplicate_customer(self):
        res_partner = self.env['res.partner']
        if self.phone:
            dup_phone = res_partner.search_count([('phone', '=', self.phone)]) + res_partner.search_count([('mobile', '=', self.phone)])
            if dup_phone:
                phone = self.phone
                partner = res_partner.search([('phone', '=', self.phone)]).name
                self.write({'phone': False})
                return {
                    'warning':  {'title': ('Trùng số điện thoại'), 'message': (("Số %s đã bị trùng với khách %s, vui lòng kiểm tra lại khách hàng") % (phone, partner)),},
                }
