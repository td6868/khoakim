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
        if vals["wp_ok"] == False:
            vals["sku_wp"] = self.create_woo_product(vals)
        return super(ProductProduct, self).create(vals)

    def write(self, values):
        wr = super(ProductProduct, self).write(values)
        if self.wp_ok == True:
            self.update_product_wp()
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
            js = update.json()
            self.write({
                'sku_wp': js['id']
            })

        status = update.status_code
        js = update.json()

        print(js['id'])
        print(status)

    @api.model
    def sync_product_wp(self):
        com_id = self.env['res.company'].search([('id', '=', 1)])
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

        if self.wp_ok:
            if self.sku_wp:
                data = {
                    "stock_quantity": self.qty_available,
                }
                update = wcapi.put("products/" + str(self.sku_wp), data)
                status = update.status_code
                js = update.json()
                print(js['id'])
                print(status)
            else:
                self.update_product_wp()

    @api.model
    def _cron_product_wp(self):
        com_id = self.env['res.company'].search([('id','=',1)])
        wp_url = com_id.wp_url
        woo_ck = com_id.woo_ck
        woo_cs = com_id.woo_cs
        
        if (wp_url == False or woo_ck == False or woo_cs == False):
            return True

        prod_vals = self.env['product.product'].search([('wp_ok', '=', True)])
        print(prod_vals)

        wcapi = API(
            url=wp_url,
            consumer_key=woo_ck,
            consumer_secret=woo_cs,
            version="wc/v3",
            timeout=30
        )
        for p in prod_vals:
            if p.sku_wp:
                data = {
                    "stock_quantity": p.qty_available,
                }
                update = wcapi.put("products/" + str(p.sku_wp), data)
                status = update.status_code
                js = update.json()
                print(js['id'])
                print(status)
            else:
                p.update_product_wp()

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
                password = str(self.phone) + '@'
                data = {
                    "username": str(self.phone),
                    "password": password,
                    "name": self.name,
                    "email": email,
                    "roles": self.roles,
                }
                r = requests.post(wp_url, auth=(wp_user, wp_pass), json=data)
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
    state = fields.Selection(selection=[
        ('draft', 'Báo giá'),
        ('waiting', 'Chờ duyệt báo giá'),
        ('sent', 'Báo giá đã gửi'),
        ('sale', 'Đơn hàng'),
        ('done', 'Đã khóa'),
        ('cancel', 'Đã hủy'),
    ], string='Trạng thái', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')

    def action_quotation_approval(self):
        sum = 0
        for l in self.order_line:
            sum += l.discount
        if sum:
            self.write({'state': 'waiting'})
            self.notify_manager()
        else:
            self.customize_sale_confirm()

    def action_accept_approval(self):
        self.customize_sale_confirm()
        self.notify_manager()

    def action_cancel_approval(self):
        self.action_draft()

    def notify_manager(self):
        if self.state == 'waiting':
            manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).parent_id
            print('run notify')
            if manager:
                for sale_approval in self.filtered(lambda hol: hol.state == 'waiting'):
                    print(sale_approval)
                    self.activity_schedule(
                        'khoakim_customize.mail_act_sale_approval_kk',
                        user_id=manager.user_id.id or self.env.uid)
            else:
                return {
                        'warning': {
                            'title': ('Đã có lỗi'),
                            'message': (("Chưa tìm được người duyệt, vui lòng liên hệ admin!")),
                        },
                    }

        self.filtered(lambda hol: hol.state in ['sale', 'done']).activity_feedback(
            ['khoakim_customize.mail_act_sale_approval_kk'])
        self.filtered(lambda hol: hol.state == 'cancel').activity_unlink(
            ['khoakim_customize.mail_act_sale_approval_kk'])

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
