# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import time

from woocommerce import API
from odoo import api, fields, models
from odoo.exceptions import Warning, UserError
import requests
import base64
import urllib.request

class SaleOrderLinesCustomize(models.Model):
    _inherit = 'sale.order.line'

    prod_image = fields.Binary(string="Ảnh sản phẩm", related="product_id.image_1920")
    qty_available = fields.Float(string="Tồn kho", related="product_id.qty_available")

class ProductProduct(models.Model):
    _inherit = 'product.template'

    url_img = fields.Char(string="URL Ảnh", required=True)
    sku_wp = fields.Char(string="ID")
    default_code = fields.Char(string="Mã nội bộ", required=True)
    wp_ok = fields.Boolean(string="Khả dụng ở website")

    @api.model
    def create(self, vals):
        if vals["wp_ok"] != True:
            vals["sku_wp"] = self.create_woo_product(vals)
        return super(ProductProduct, self).create(vals)

    def write(self, values):
        wr = super(ProductProduct, self).write(values)
        if self.wp_ok == True:
            self.update_product_wp(values)
        return wr

    @api.onchange('default_code')
    def action_duplicate_code(self):
        if self.type == 'product':
            if self.default_code:
                dup_code = self.env['product.product'].search([('default_code', '=', self.default_code)])
                if dup_code:
                    code = self.default_code
                    self.default_code = False
                    return {
                        'warning': {
                                        'title': ('Trùng sản phẩm'),
                                        'message': (("Mã %s đã bị trùng với sản phẩm %s, vui lòng chọn mã khác") % (code, dup_code))
                                    },
                    }

    @api.onchange('url_img')
    def onchange_image(self):
        if self.url_img:
            get_img = urllib.request.urlopen(self.url_img).read()
            img_b64 = base64.encodestring(get_img)
            self.write({
                "image_1920": img_b64,
            })

    def create_woo_product(self, vals):
        com_id = self.env.company
        wp_url = com_id.wp_url
        woo_ck = com_id.woo_ck
        woo_cs = com_id.woo_cs

        if (wp_url == False or woo_ck == False or woo_cs == False):
            return True

        wcapi = API(
            url=wp_url,
            consumer_key=woo_ck,
            consumer_secret=woo_cs,
            version="wc/v3",
            timeout=30
        )

        # print(vals['name'])

        data = {
                "name": vals['name'],
                "type": "simple",
                "regular_price": str(vals['list_price']),
                "description": vals['description'] or "Chưa được cập nhật",
                "short_description": vals['description'] or "Chưa được cập nhật",
                "manage_stock": 1,
                "stock_quantity": "10",
                "sku": vals['default_code'],
                "images": [
                    {
                        "src": vals['url_img']
                    },
                ]
            }

        # if self.sku_wp:
        #     wcapi.put("products" + str(self.id), data).json()
        # else:
        post = wcapi.post("products", data)
        status = post.status_code
        js = post.json()
        print(status)
        if status == 201:
            return js["id"]
        else:
            return False

    def update_product_wp(self):
        com_id = self.env.company
        wp_url = com_id.wp_url
        woo_ck = com_id.woo_ck
        woo_cs = com_id.woo_cs

        if (wp_url == False or woo_ck == False or woo_cs == False):
            return True

        wcapi = API(
            url=wp_url,
            consumer_key=woo_ck,
            consumer_secret=woo_cs,
            version="wc/v3",
            timeout=30
        )

        data = {
            # "name": values['name'],
            "name": self.name,
            "type": "simple",
            "regular_price": str(self.list_price),
            "description": self.description or "Chưa được cập nhật",
            "short_description": self.description or "Chưa được cập nhật",
            "manage_stock": 1,
            "stock_quantity": self.qty_available or "10",
            "sku": self.default_code,
            "images": [
                {
                    "src": self.url_img
                },
            ]
        }

        if self.sku_wp:
            update = wcapi.put("products/" + str(self.sku_wp), data)
        else:
            update = wcapi.post("products", data)

        status = update.status_code
        js = update.json()
        print(js)
        print(status)

    def sync_product_wp(self):
        for p in self:
            if p.sku_wp == False:
                wp_url = ''
                woo_ck = ''
                woo_cs = ''

                wcapi = API(
                    url=wp_url,
                    consumer_key=woo_ck,
                    consumer_secret=woo_cs,
                    version="wc/v3"
                )

                data = {
                    "name": p.name,
                    "type": "simple",
                    "regular_price": p.list_price,
                    "description": p.description,
                    "short_description": p.description,
                    "manage_stock": 1,
                    "stock_quantity": p.qty_available or "10",
                    "sku": p.default_code,
                    "images": [
                        {
                            "src": p.url_img
                        },
                    ]
                }

                if p.sku_wp:
                    update = wcapi.put("products" + str(p.sku_wp), data)
                else:
                    update = wcapi.post("products", data)
                    status = update.status_code
                    js = update.json()
                    if status == 201:
                        p.write({
                            'sku_wp': js["id"],
                        })

class ResPartnerCustomize(models.Model):
    _inherit = 'res.partner'

    phone = fields.Char(string="Số điện thoại", required=True)
    roles = fields.Selection([
        ('daily1', 'Đại lý cấp 1'),
        ('daily2', 'Đại lý cấp 2'),
        ('daily3', 'Đại lý cấp 3')
        ], string='Cấp đại lý', required=True)

    @api.onchange('phone')
    def action_duplicate_customer(self):
        res_partner = self.env['res.partner']
        if self.phone:
            dup_phone = res_partner.search_count([('phone', '=', self.phone)])
            if dup_phone:
                phone = self.phone
                partner = res_partner.search([('phone', '=', self.phone)]).name
                self.write({'phone': False})
                return {
                    'warning':  {
                                    'title': ('Trùng số điện thoại'),
                                    'message': (("Số %s đã bị trùng với khách %s, vui lòng kiểm tra lại khách hàng") % (phone, partner)),
                                 },
                }

    def create_acc_distributor(self):
        com_id = self.env.company
        wp_user = com_id.wp_user
        wp_pass = com_id.wp_pass

        if (com_id.wp_url or wp_user or wp_pass):
            wp_url = com_id.wp_url + '/wp-json/wp/v2/users'

            if self.email:
                email = self.email
            else:
                email = self.phone + '@khoakim.com.vn'

            if (self.phone and self.roles):
                password = str(self.phone) + '@abc'
                print(password)
                data = {
                    "username": str(self.phone),
                    "password": password,
                    "name": self.name,
                    "email": email,
                    "roles": self.roles,
                }
                r = requests.post(wp_url, auth=(wp_user, wp_pass), json=data)
                print(r.text)
                if (r.status_code == '201'):
                    return {
                        'warning': {
                            'title': ('Tạo tài khoản thành công'),
                            'message': (("Tài khoản của khách hàng đã được tạo thành công! Với tên tài khoản là %s và mật khẩu là %s") % (self.phone, self.phone))
                        },
                    }
                else:
                    return {
                        'warning': {
                            'title': ('Đã có lỗi'),
                            'message': (("Đã có lỗi %s . Liên hệ với admin để giải đáp!") % (r.status_code)),
                        },
                    }
        return UserError('Lỗi chưa có thông tin về website Đại lý. Hãy vào công ty để khai báo!')


class SaleOrderCustomize(models.Model):
    _inherit = 'sale.order'

    total_due = fields.Monetary(string="Công nợ hiện tại", related="partner_id.total_due")

    def customize_sale_confirm(self):
        self.action_confirm()
        iv = self._create_invoices(final=True)
        if iv:
            iv.action_post()
            return self.env['account.payment'] \
                .with_context(active_ids=iv.ids, active_model='account.move', active_id=iv.id) \
                .action_register_payment()
        else:
            return {
                'warning': {
                                'title': ('Kiểm tra lại cấu hình sản phẩm'),
                                'message': ("Không thể tạo hóa đơn theo đơn hàng"),
                            },
            }

class ResCompanyCustomize(models.Model):
    _inherit = 'res.company'

    wp_url = fields.Char(string='Link website')
    wp_user = fields.Char(string='Tài khoản WP')
    wp_pass = fields.Char(string='Mật khẩu WP')
    woo_ck = fields.Char(string='Keys Woocommerce')
    woo_cs = fields.Char(string='Secret Woocommerce')

# class WPSetting(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     wp_url = fields.Char(string='URL website')
#     wp_user = fields.Char(string='Tài khoản WP')
#     wp_pass = fields.Char(string='Mật khẩu WP')
#     woo_ck = fields.Char(string='Keys Woocommerce')
#     woo_cs = fields.Char(string='Secret Woocommerce')
