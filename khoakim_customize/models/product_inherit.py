# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrderLinesCustomize(models.Model):
    _inherit = 'sale.order.line'

    prod_image = fields.Binary(string="Ảnh sản phẩm", related="product_id.image_1920")
    qty_available = fields.Float(string="Tồn kho", related="product_id.qty_available")

    # @api.onchange('product_id')
    # def get_image_qty_prod(self):
    #     for rec in self:
    #         if rec.product_id:
    #             rec.prod_image = rec.product_id.image_1024
    #             rec.qty_available = rec.product_id.qty_available
    #         else:
    #             rec.prod_image = 0
    #             rec.qty_available = 0