# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import ssl
from vietnam_number import n2w
import string
import random
from woocommerce import API
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
import requests
import base64
import urllib.request
import gspread
import time
from gspread.cell import Cell
import json

INFO = {
          "type": "service_account",
          "project_id": "gsodsync",
          "private_key_id": "23521eba50f0f7e57f857777fb40dbc40a0227dc",
          "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDQ3Pkn7iuLvfj1\nQ3Q9IRYj847mxCzQM+vxCQxFN0q8zISwf3C0AWvoacDc/XmMaRLd5bno3Eg3NmFi\nt1JePA7yszZ0eBX5+EvNgoLCafmSVeWMZyyV4C92bqu8QZ/MXe7go+6Nn1z4khni\nXKquyj1k/XJj+hZJQ5H5hsCDEKwFxKcAKEn4XzBYer+bntjcBrvt0BW9A/QiB/nY\niqQvu+QwZ11bTsK6felHLayzeckgzeh99JWR7GKnOMvXcujh6F2igzAlrkr1SeV3\nKWLQ8I8zF7vSPxQziSztlDWnzH5Twa2zqsoSa/STB2kFjikBGKDiaiXny+EHl2YL\nmhgW8jzhAgMBAAECggEALDTI62Gmh9Iykj6vqIyLMhrHwSH+VibXJlIC7ddxExq6\nbtzaTs8KNsvDTUK86jIHEz4fJiERi9YPsKQaY+WUSFwUB3yvMhQSfzHDWUCy2P0j\nM59WuXYUtZ1g7dx55Phwqc0onYMAW4AYyGdSnOIjMm/OOUjiVKlfiQ+zSUpLDoEZ\n2Ua1wCaLsWqPtKMZjhM3M8jupCLjZBV38DhoRN/ykj5Cn4XGq54O5ZYRLswDhkYP\nHxCH3XrzahdrYv0B2dLMru8HOhs75wbNYDwY9NV9cqtWKnBHHuqcIeGlXiPwH+4J\ngVfVcPDb46ilXJahPrc8GQRktXf3LHMpQKfA8GEz/QKBgQDxnjPJAkRL1AvTKO3o\nBoj2RhlUAYvNhClR/VsCEAsA7VUWR5AMXxdEjSsMPWXnLorQgWw9duz0StMA1R7N\nV+xtbrPzi+Om1fl3+LspqWgHCr9eu9bcveSFuFtd+arcNEyhtV3thI82hcZab0J0\nfm1igWSR+DMWKXsOoOfqTutczwKBgQDdS6Z0LJAEDxY5Ep0whYbUKU7OVhm4rRkt\ntAQ8GFdxXi+f8he9SgVHn7FoP1pJEma5eOAjuk+3NH/TRQ6uD/948jRfEtpYx/Mz\nPyyEZl3y/r/1eyFo9E9i98S21TcOOIRk3ozQlJyObSPzrJvhS9P15gYB5eBtB+Nt\n6vHuu+YXTwKBgQDrOaSaze0lkZPNiKxM1ofikw43faXYeBEuNCS01l+QEH5kyVjQ\n4oapg3HkYaXisqoMIeP51t0LXAkeZ12sdivDwiHJOmhwVSKhDPNRtQ6ExI7YsLCW\niPyAvqGc1OLlrLjqOcLu6L3wS7527phZB3iAjQ4XGfbKXani7P27XAfBewKBgQDN\nHVaOrdNa/8TgZ6FtHQbI1fTmiaXTqBYDZ6zZKtK6EMvh29onKFnWdm1QrA/6VOUE\nGsbeNs22iSHF6Gdf7RIlv5HNYcMisUp5gJ+5pMyF85xnY5anGnQOzor10JD0TGxi\ntmkc1/J4jS7aqG3fmJJBhNCip7iqNrqV4kQWvPDbPwKBgG1TjB99rHM6WY3GoBHd\nz6FJcdJXRpjYpEKE2nWHt8rec9P61fYIrYnk/4zWHm0kbQlMxUbVoaiuzhAa0XcH\nge3VJpBmjvOqJDtcV7EyOadAIw6HgXSeKUwosvl/o4l/v7ByDFkuth4tLE3Fo7Sg\nCK5m9S/urxMLC9As8J45S21q\n-----END PRIVATE KEY-----\n",
          "client_email": "odoogsheetkk@gsodsync.iam.gserviceaccount.com",
          "client_id": "116816502838220913532",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/odoogsheetkk%40gsodsync.iam.gserviceaccount.com"
        }
SA = gspread.service_account_from_dict(INFO)
WB = SA.open("SyncOdooProd")
WS_PROD = WB.worksheet("MasterProd")
WS_CATG = WB.worksheet("MasterCatg")
# WP_URL =
WP_PROD = "products"
WP_CATG = "products/categories"
WP_ATTR = "products/attributes"
WP_TAGS = "products/tags"
WP_TERMS = "/terms"


def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    type_pl = fields.Selection([
        ('main', 'Bảng giá niêm yết'),
        ('policy', 'Theo chính sách'),
        ('non_policy', 'Không theo chính sách')
    ], string="Loại bảng giá", default='main', required=True)
    # def_pl_id = fields.Many2one('product.pricelist', string="Bảng giá NY", domain=[('type_pl', '=', 'main')])
    discount = fields.Float(string='Chiết khấu theo bảng giá (%)', tracking=True)
    # type_dics = fields.Selection([
    #     ('perc', 'Phần trăm'),
    #     ('fix', 'Tiền cố định'),
    # ], string='Loại chiết khấu')
    # catg_id = fields.Many2one('product.category', string='Danh mục SP', tracking=True, onchange=True)
    # catg_disc = fields.Float(string='Chiết khấu', tracking=True)
    roles = fields.Selection([
        ('daily1', 'Đại lý cấp 1'),
        ('daily2', 'Đại lý cấp 2'),
        ('daily3', 'Đại lý cấp 3'),
        ('customer', 'Khách hàng lẻ'),
    ], string='Cấp đại lý', default='customer', required=True)
    count_pl = fields.Integer(string='Số lượng SP', compute='count_all_pl')

    # def write(self, vals):
    #     super(Pricelist, self).write(vals)

    def action_view_pricelist(self):
        self.ensure_one()
        view_id = self.env.ref('khoakim_customize.view_price_list_item_kk')
        search_view_id = self.env.ref('khoakim_customize.view_price_list_item_filter_kk')
        result = {
                    "name": "Bảng giá chi tiết",
                    "res_model": "product.pricelist.item",
                    "type": "ir.actions.act_window",
                    'view_mode': 'tree',
                    "domain": [('pricelist_id.id', '=', self.id)],
                    "context": {"create": False},
                    "view_id": view_id.ids,
                    "search_view_id": search_view_id.ids,
                }
        return result

    def count_all_pl(self):
        count = self.env['product.pricelist.item'].search_count([('pricelist_id.id', '=', self.id)])
        self.count_pl = count

    # def action_price_categ(self):
    #     if self.catg_id and self.catg_disc and self.type_dics:
    #         for l in self.item_ids:
    #             categ_ids = self.env['product.category'].search([('id', 'child_of', [self.catg_id.id])])
    #             for cid in categ_ids:
    #                 if l.product_tmpl_id.categ_id.id == cid.id:
    #                     cur_price = l.fixed_price
    #                     if self.type_dics == 'perc':
    #                         l.fixed_price = ((100.00 - self.catg_disc) / 100.00) * cur_price
    #                     elif self.type_dics == 'fix':
    #                         l.fixed_price = cur_price - self.catg_disc
    #         self.write({
    #             'catg_id': False,
    #             'type_dics': False,
    #             'catg_disc': False
    #         })
    #
    # def _update_price_policy(self):
    #     if self.discount:
    #         for l in self.item_ids:
    #             cur_price = l.fixed_price
    #             l.fixed_price = ((100.00 - self.discount) / 100.00) * cur_price
    #
    # def action_update_main_price(self):
    #     pl = self.env['product.pricelist']
    #     pl_ids = pl.search([('def_pl_id', '=', self.id)])
    #     pl_item_ids = []
    #     pl_update = ''
    #     for item in self.item_ids:
    #         pl_item_ids.append((0, item.id,
    #                             {
    #                                 'product_tmpl_id': item.product_tmpl_id.id,
    #                                 'product_id': item.product_id.id,
    #                                 'min_quantity': item.min_quantity,
    #                                 'fixed_price': ((100.00 - self.discount) / 100.00) * item.fixed_price,
    #                                 'date_start': item.date_start,
    #                                 'date_end': item.date_end
    #                             }))
    #     for pl_id in pl_ids:
    #         if pl_id.item_ids:
    #             for i in pl_id.item_ids:
    #                 i.unlink()
    #         pl_id.write({
    #             'item_ids': pl_item_ids,
    #             })
    #         pl_id._update_price_policy()
    #         pl_update += str(pl_id.name) + ', '
    #     return {
    #                 'warning': {
    #                     'title': ('Đã hoàn thành'),
    #                     'message': (("Đã cập nhật các bảng giá sau %s") % (pl_update))
    #                 },
    #             }

    # def action_update_price(self):
    #         pl_item_ids = []
    #         for item in self.def_pl_id.item_ids:
    #             pl_item_ids.append((0, item.id,
    #             {
    #                 'product_tmpl_id': item.product_tmpl_id.id,
    #                 'product_id': item.product_id.id,
    #                 'min_quantity': item.min_quantity,
    #                 'fixed_price': ((100.00 - self.discount) / 100.00) * item.fixed_price ,
    #                 'date_start': item.date_start,
    #                 'date_end': item.date_end
    #             }))
    #         if self.item_ids:
    #             for i in self.item_ids:
    #                 i.unlink()
    #         self.write({
    #             'item_ids': pl_item_ids,
    #         })

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    prod_image = fields.Binary(string="Ảnh sản phẩm", related="product_id.image_1920")
    qty_available = fields.Float(string="Tồn kho", related="product_id.qty_available")
    virtual_available = fields.Float(string="Khả dụng", related="product_id.virtual_available")
    virtual_qty = fields.Char(string="TKKD/ TKTT", compute="_virtual_qty")
    cus_discount = fields.Float(string='C.Khấu ($)')
    new_price_unit = fields.Float(string='Giá trước CK', readonly=False)
    note = fields.Char(string='Ghi chú')
    cur_price_unit = fields.Char(string='BG cũ')

    @api.depends("qty_available", "virtual_available")
    def _virtual_qty(self):
        for line in self:
            virtual_qty = ''
            if line.product_id:
                virtual_qty = ("%s/%s") % (line.virtual_available, line.qty_available)
            line.virtual_qty = virtual_qty

    @api.onchange("discount")
    def _onchange_discount(self):
        if self.cus_discount and self.discount:
            self.update({
                    'cus_discount': 0.0,
                })

    @api.onchange("cus_discount")
    def _onchange_cusdiscount(self):
        if self.discount and self.cus_discount:
            self.update({
                    'discount': 0.0,
                })

    @api.depends("product_uom_qty", "discount", "price_unit", "tax_id", "cus_discount")
    def _compute_amount(self):
        vals = {}
        res = {}
        for line in self:
            old_price = line.new_price_unit or line.price_unit
            real_price = line.new_price_unit * (1 - (line.discount or 0.0) / 100.0) - (
                    line.cus_discount or 0.0
            )
            if real_price >= 0.0:
                vals[line] = {
                    "price_unit": real_price,
                    "new_price_unit": old_price,
                }
                line.update({"price_unit": real_price})
                res = super(SaleOrderLine, self)._compute_amount()
            else:
                vals[line] = {
                    "cus_discount": 0.0,
                    "discount": 0.0,
                }
                res = {
                            'warning': {
                                'title': ('Số tiền chiết khấu không phù hợp'),
                                'message': (("Số tiền chiết khấu không thể nhỏ hơn 0.0"))
                            },
                        }
            for line in vals.keys():
                line.update(vals[line])
        return res

    @api.onchange('product_id', 'order_partner_id')
    def current_price_partner(self):
        product = self.env['sale.order.line'].search([('order_partner_id', '=', self.order_partner_id.id),
                                                    ('state', 'in', ['sale','done']),
                                                    ('product_id', '=', self.product_id.id)], order='order_id asc', limit=1)
        price = 'Chưa BG'
        if product:
            price = product.price_unit
        self.write({'cur_price_unit': price})

class AccountMove(models.Model):
    _inherit = "account.move"

    pst_by_word = fields.Char(string="Số tiền bằng chữ", compute='_compute_subtotal_word')

    @api.depends('amount_total')
    def _compute_subtotal_word(self):
        if self.amount_total:
            pst_word = n2w(str(self.amount_total/10))
            self.pst_by_word = pst_word.capitalize() + ' đồng'
        else:
            self.pst_by_word = ''

    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        vals = {}
        for line in self.invoice_line_ids.filtered("cus_discount"):
            vals[line] = {"price_unit": line.price_unit}
            price_unit = line.price_unit - line.cus_discount
            line.update({"price_unit": price_unit})
        res = super(AccountMove, self)._recompute_tax_lines(
            recompute_tax_base_amount=recompute_tax_base_amount
        )
        for line in vals.keys():
            line.update(vals[line])
        return res

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    cus_discount = fields.Float(string='C.Khấu ($)')

    @api.onchange("cus_discount")
    def _onchange_discount_percent(self):
        if self.cus_discount:
            self.write({
                'discount': 0.0,
            })

    @api.onchange("discount")
    def _onchange_discount_fix(self):
        if self.discount:
            self.write({
                'cus_discount': 0.0,
            })

    @api.onchange("quantity", "discount", "price_unit", "tax_ids", "cus_discount")
    def _onchange_price_subtotal(self):
        return super(AccountMoveLine, self)._onchange_price_subtotal()

    @api.model
    def _get_price_total_and_subtotal_model(
        self,
        price_unit,
        quantity,
        discount,
        currency,
        product,
        partner,
        taxes,
        move_type,
    ):
        if self.cus_discount != 0:
            discount = ((self.cus_discount) / price_unit) * 100 or 0.00
        return super(AccountMoveLine, self)._get_price_total_and_subtotal_model(
            price_unit, quantity, discount, currency, product, partner, taxes, move_type
        )

    @api.model
    def _get_fields_onchange_balance_model(
        self,
        quantity,
        discount,
        amount_currency,
        move_type,
        currency,
        taxes,
        price_subtotal,
        force_computation=False,
    ):
        if self.cus_discount:
            discount = ((self.cus_discount) / self.price_unit) * 100 or 0.00
        return super(AccountMoveLine, self)._get_fields_onchange_balance_model(
            quantity,
            discount,
            amount_currency,
            move_type,
            currency,
            taxes,
            price_subtotal,
            force_computation=force_computation,
        )

    @api.model_create_multi
    def create(self, vals_list):
        prev_discount = []
        for vals in vals_list:
            if vals.get("cus_discount"):
                prev_discount.append(
                    {"cus_discount": vals.get("cus_discount"), "discount": 0.00}
                )
                fixed_discount = (
                    vals.get("cus_discount") / vals.get("price_unit")
                ) * 100
                vals.update({"discount": fixed_discount, "cus_discount": 0.00})
            elif vals.get("discount"):
                prev_discount.append({"discount": vals.get("discount")})
        res = super(AccountMoveLine, self).create(vals_list)
        i = 0
        for rec in res:
            if rec.discount and prev_discount:
                rec.write(prev_discount[i])
                i += 1
        return res

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    url_img = fields.Char(string="URL Ảnh")
    sku_wp = fields.Char(string="ID WP")
    default_code = fields.Char(string="Mã nội bộ", compute='_gen_product_code', store=True)
    wp_ok = fields.Boolean(string="Khả dụng ở website")
    prod_code = fields.Char(string="Mã SP/NSX", required=False)
    sale_ok = fields.Boolean('Có thể bán', default=False)
    purchase_ok = fields.Boolean('Có thể mua', default=False)
    appr_state = fields.Boolean('Trạng thái duyệt', default=False)
    url_img2 = fields.Char(string="URL Ảnh 2")
    url_img3 = fields.Char(string="URL Ảnh 3")
    url_img4 = fields.Char(string="URL Ảnh 4")
    url_img5 = fields.Char(string="URL Ảnh 5")
    # product_ok = fields.Boolean('Là sản phẩm', default=False)

    @api.model
    def create(self, vals):
        rec = super(ProductTemplate, self).create(vals)
        # if self.wp_ok == True:
        #     self.update_product_wp()
        check_pass = self.check_perm_product_temp()
        if check_pass:
            self.write({'appr_state': True})
        return rec

    @api.onchange('prod_code')
    def action_duplicate_code(self):
        if self.type == 'product':
            if self.prod_code:
                dup_code = self.env['product.template'].search([('prod_code', '=', self.prod_code)])
                if dup_code:
                    code = self.prod_code
                    self.prod_code = False
                    return {
                        'warning': {
                                        'title': ('Trùng sản phẩm'),
                                        'message': (("Mã %s đã bị trùng với sản phẩm %s, vui lòng chọn mã khác") % (code, dup_code.name))
                                    },
                    }

    @api.depends('categ_id', 'prod_code')
    def _gen_product_code(self):
        for prod in self:
            if prod.categ_id:
                prod.default_code = '%s%s' % (prod.categ_id.cate_code or '', prod.prod_code or '')
            else:
                prod.default_code = prod.prod_code or ''

    @api.onchange('url_img')
    def onchange_image(self):
        if self.url_img:
            context = ssl._create_unverified_context()
            get_img = urllib.request.urlopen(self.url_img, context=context).read()
            img_b64 = base64.b64encode(get_img)
            self.write({
                "image_1920": img_b64,
                "image_1024": img_b64,
                "image_128": img_b64,
                "image_256": img_b64,
                "image_512": img_b64,
            })

    def check_perm_product_temp(self):
        group_pass = 'khoakim_customize.group_approval_product_temp'
        user_id = self.env.user
        if user_id.has_group(group_pass):
            return True
        return False

    def prod_temp_approvaled(self):
        check_perm = self.check_perm_product_temp()
        if check_perm:
            for p in self:
                p.write({
                    'sale_ok': True,
                    'purchase_ok': True,
                    'appr_state': True,
                })
        else:
            return {
                'warning': {
                    'title': ('Lỗi người dùng'),
                    'message': (("Người dùng không được quyền truy cập"))
                },
            }

    def prod_temp_approvaled_batch(self):
        for p in self.browse(self.env.context['active_ids']):
            p.prod_temp_approvaled()

    def prod_temp_deny_batch(self):
        check_perm = self.check_perm_product_temp()
        if check_perm:
            for p in self.browse(self.env.context['active_ids']):
                p.prod_temp_deny()
        else:
            return {
                'warning': {
                    'title': ('Lỗi người dùng'),
                    'message': (("Người dùng không được quyền truy cập"))
                },
            }

    def prod_temp_deny(self):
        check_perm = self.check_perm_product_temp()
        if check_perm:
            for p in self:
                p.write({'active': False,
                         'sale_ok': False,
                         'purchase_ok': False,
                         'appr_state': False,
                         })
        else:
            return {
                'warning': {
                    'title': ('Lỗi người dùng'),
                    'message': (("Người dùng không được quyền truy cập"))
                },
            }

    # def create_woo_product(self, vals):
    #     com_id = self.env.company
    #     wp_url = com_id.wp_url
    #     woo_ck = com_id.woo_ck
    #     woo_cs = com_id.woo_cs
    #
    #     if (wp_url == False or woo_ck == False or woo_cs == False):
    #         return True
    #
    #     wcapi = API(
    #         url=wp_url,
    #         consumer_key=woo_ck,
    #         consumer_secret=woo_cs,
    #         version="wc/v3",
    #         timeout=30
    #     )
    #
    #     # print(vals['name'])
    #
    #     data = {
    #             "name": vals['name'],
    #             "type": "simple",
    #             "regular_price": str(vals['list_price']),
    #             "description": vals['description'] or "Chưa được cập nhật",
    #             "short_description": vals['description'] or "Chưa được cập nhật",
    #             "manage_stock": 1,
    #             "stock_quantity": "10",
    #             "sku": vals['default_code'],
    #             "images": [
    #                 {
    #                     "src": vals['url_img']
    #                 },
    #             ]
    #         }
    #
    #     # if self.sku_wp:
    #     #     wcapi.put("products" + str(self.id), data).json()
    #     # else:
    #     post = wcapi.post("products", data)
    #     status = post.status_code
    #     js = post.json()
    #     print(status)
    #     if status == 201:
    #         return js["id"]
    #     else:
    #         id = ''
    #         return id

    # def update_product_wp(self):
    #     com_id = self.env.company
    #     wp_url = com_id.wp_url
    #     woo_ck = com_id.woo_ck
    #     woo_cs = com_id.woo_cs
    #     sku_wp = ''
    #
    #     if (wp_url == False or woo_ck == False or woo_cs == False):
    #         return sku_wp
    #
    #     wcapi = API(
    #         url=wp_url,
    #         consumer_key=woo_ck,
    #         consumer_secret=woo_cs,
    #         version="wc/v3",
    #         timeout=30
    #     )
    #
    #     data = {
    #         # "name": values['name'],
    #         "name": self.name,
    #         "type": "simple",
    #         "regular_price": str(self.list_price),
    #         "description": self.description or "Chưa được cập nhật",
    #         "short_description": self.description or "Chưa được cập nhật",
    #         "manage_stock": 1,
    #         "stock_quantity": self.qty_available or "10",
    #         "sku": self.default_code,
    #         "images": [
    #             {
    #                 "src": self.url_img or ''
    #             },
    #         ]
    #     }
    #
    #     if self.sku_wp:
    #         update = wcapi.put("products/" + str(self.sku_wp), data)
    #     else:
    #         update = wcapi.post("products", data)
    #
    #     status = update.status_code
    #     js = update.json()
    #
    #     if status == 201:
    #         js = update.json()
    #         self.write({
    #             'sku_wp': js['id']
    #         })
    #
    #     print(js['id'])
    #     print(status)

    # @api.model
    # def sync_product_wp(self):
    #     com_id = self.env['res.company'].search([('id', '=', 1)])
    #     wp_url = com_id.wp_url
    #     woo_ck = com_id.woo_ck
    #     woo_cs = com_id.woo_cs
    #     sku_wp = ''
    #
    #     if (wp_url == False or woo_ck == False or woo_cs == False):
    #         return sku_wp
    #
    #     wcapi = API(
    #         url=wp_url,
    #         consumer_key=woo_ck,
    #         consumer_secret=woo_cs,
    #         version="wc/v3",
    #         timeout=30
    #     )
    #
    #     if self.wp_ok:
    #         if self.sku_wp:
    #             data = {
    #                 "stock_quantity": self.qty_available,
    #             }
    #             update = wcapi.put("products/" + str(self.sku_wp), data)
    #             status = update.status_code
    #             js = update.json()
    #             print(js['id'])
    #             print(status)
    #         else:
    #             self.update_product_wp()

    # @api.model
    # def _cron_product_wp(self):
    #     com_id = self.env['res.company'].search([('id','=',1)])
    #     wp_url = com_id.wp_url
    #     woo_ck = com_id.woo_ck
    #     woo_cs = com_id.woo_cs
    #     sku_wp = ''
    #
    #     if (wp_url == False or woo_ck == False or woo_cs == False):
    #         return sku_wp
    #
    #     prod_vals = self.env['product.product'].search([('wp_ok', '=', True)])
    #     print(prod_vals)
    #
    #     wcapi = API(
    #         url=wp_url,
    #         consumer_key=woo_ck,
    #         consumer_secret=woo_cs,
    #         version="wc/v3",
    #         timeout=30
    #     )
    #     for p in prod_vals:
    #         if p.sku_wp:
    #             data = {
    #                 "stock_quantity": p.qty_available,
    #                 "regular_price": str(p.list_price),
    #             }
    #             update = wcapi.put("products/" + str(p.sku_wp), data)
    #             status = update.status_code
    #             js = update.json()
    #             print(js['id'])
    #             print(status)
    #         else:
    #             p.update_product_wp()

class ProductAttributeValues(models.Model):
    _inherit = 'product.attribute.value'

    acode = fields.Char(string='Mã biến thể', required=True)
    attr_term_wp = fields.Char(string='ID')

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    attr_wp = fields.Char(string='ID')

    # def update_attrs_wp(self):
    #     com_id = self.env.company
    #     wp_url = com_id.wp_url
    #     woo_ck = com_id.woo_ck
    #     woo_cs = com_id.woo_cs
    #
    #     if (wp_url == False or woo_ck == False or woo_cs == False):
    #         return True
    #
    #     wcapi = API(
    #         url=wp_url,
    #         consumer_key=woo_ck,
    #         consumer_secret=woo_cs,
    #         version="wc/v3",
    #         timeout=30
    #     )
    #
    #     data = {
    #         "name": self.name,
    #         "type": "select",
    #         "order_by": "menu_order",
    #         "has_archives": True
    #     }
    #
    #     if self.cate_id:
    #         update = wcapi.put("products/attributes/" + str(self.cate_id), data)
    #         status = update.status_code
    #     else:
    #         update = wcapi.post("products/attributes", data)
    #         status = update.status_code
    #         if status == 201:
    #             js = update.json()
    #             self.cate_id = js['id']

class ProductCategory(models.Model):
    _inherit = 'product.category'

    ccode = fields.Char(string="Mã nhóm sản phẩm", required=True)
    cate_code = fields.Char(string="Mã nhóm", compute='_gene_code_cate', store=True)
    sku_wp = fields.Char(string="WP ID")
    wp_ok = fields.Char(string="Khả dụng trên website")

    @api.depends('ccode', 'parent_id')
    def _gene_code_cate(self):
        for cate in self:
            if cate.parent_id:
                cate.cate_code = '%s%s' % (cate.parent_id.cate_code or '', cate.ccode or '')
            else:
                cate.cate_code = cate.ccode or ''

    @api.onchange('ccode')
    def action_duplicate_categ_code(self):
        if self.ccode:
            dup_code = self.env['product.category'].search([('ccode', '=', self.ccode)])
            if dup_code:
                code = self.ccode
                self.ccode = False
                return {
                        'warning': {
                            'title': ('Trùng nhóm sản phẩm'),
                            'message': (("Mã %s đã bị trùng với nhóm sản phẩm %s, vui lòng chọn mã khác") % (code, dup_code.name))
                        },
                    }

    # def update_categ_wp(self):
    #     com_id = self.env.company
    #     wp_url = com_id.wp_url
    #     woo_ck = com_id.woo_ck
    #     woo_cs = com_id.woo_cs
    #
    #     if (wp_url == False or woo_ck == False or woo_cs == False or self.wp_ok == False):
    #         return True
    #
    #     wcapi = API(
    #         url=wp_url,
    #         consumer_key=woo_ck,
    #         consumer_secret=woo_cs,
    #         version="wc/v3",
    #         timeout=30
    #     )
    #
    #     data = {
    #         "name": self.name,
    #         "parent": self.parent_id.cate_id or 0,
    #         "description": "",
    #     }
    #
    #     if self.cate_id:
    #         update = wcapi.put("products/categories/" + str(self.cate_id), data)
    #         status = update.status_code
    #     else:
    #         update = wcapi.post("products/categories", data)
    #         status = update.status_code
    #         if status == 201:
    #             js = update.json()
    #             self.cate_id = js['id']
    #     print(status)

    # Đồng bộ hoá gsheet
    def sync_odoo_catg_gsheet(self):
        catg_ids = self.browse(self.env.context['active_ids'])
        time_update = fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for rec in catg_ids:
            cell = WS_CATG.find(query=str(rec.id), in_row=2)
            vals = [time_update, rec.id, rec.name, rec.ccode, rec.parent_id.name]
            if cell:
                row = cell.row
            else:
                row = next_available_row(WS_CATG)
            cells=[]
            for i in range(len(vals)):
                cells.append(Cell(row=int(row), col=i + 1, value=vals[i]))
            WS_CATG.update_cells(cells)
            time.sleep(2)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    prod_code = fields.Char(string="Mã SP/SX", compute='_get_temp_prod')
    default_code = fields.Char(string="Mã nội bộ", compute='_gen_product_attrs_code', store=True)
    sku_wp = fields.Char(string="ID WP")

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        # self._gen_product_attrs_code()
        return res

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        # self._gen_product_attrs_code()
        return res

    def _get_temp_prod(self):
        for p in self:
            if p.product_tmpl_id:
                p.prod_code = p.product_tmpl_id.prod_code or ''

    @api.depends('product_template_attribute_value_ids', 'prod_code', 'product_tmpl_id.default_code')
    def _gen_product_attrs_code(self):
        for prod in self:
            code = prod.product_tmpl_id.default_code or ''
            attrs = prod.product_template_attribute_value_ids
            if attrs:
                b = []
                for s in attrs:
                    b.append((s.attribute_id.sequence, s.product_attribute_value_id.acode))
                d = sorted(b)
                for c in d:
                    code += c[1] or ''
                prod.default_code = code

    @api.onchange('url_img')
    def onchange_image(self):
        if self.url_img:
            get_img = urllib.request.urlopen(self.url_img).read()
            img_b64 = base64.b64encode(get_img)
            self.write({
                "image_1920": img_b64,
                "image_1024": img_b64,
                "image_128": img_b64,
                "image_256": img_b64,
                "image_512": img_b64,
                "image_variant_1920": img_b64,
                "image_variant_1024": img_b64,
                "image_variant_512": img_b64,
                "image_variant_256": img_b64,
                "image_variant_128": img_b64,
            })

    # Đồng bộ hoá gsheet
    def sync_odoo_prod_gsheet(self):
        prod_ids = self.browse(self.env.context['active_ids'])
        time_update = fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for rec in prod_ids:
            cell = WS_PROD.find(query=str(rec.id), in_column=2)
            attr_prod = rec.product_template_attribute_value_ids
            attrs = ''
            brand = 'Không có'
            name = rec.name
            if attr_prod:
                for a in attr_prod:
                    if a.attribute_id.sequence == 0:
                        brand = a.name
                    attrs += '<p>' + a.attribute_id.name + ' : ' + a.name + '</p>'
                    name += ' ' + a.name
            vals = [time_update, rec.id, rec.url_img or '', rec.url_img or rec.product_tmpl_id.url_img or '', name, rec.prod_code, rec.categ_id.name, brand, attrs, rec.list_price, rec.virtual_available]
            if cell:
                row = cell.row
            else:
                row = next_available_row(WS_PROD)
            # WS_PROD.update_cell(values=vals, row=int(row))
            cells = []
            for i in range(len(vals)):
                cells.append(Cell(row=int(row), col=i + 1, value=vals[i]))
            WS_PROD.update_cells(cells)
            time.sleep(2)

    #authen wp
    def wp_auth(self):
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
        return wcapi

    #create wp product
    def create_wp_product(self):
        for rec in self:
            wpapi = rec.wp_auth()
            name = rec.name
            categ_id = rec.categ_id.sku_wp
            tags = []
            for v in rec.product_template_attribute_value_ids:
                name += ' ' + v.attribute_id.name
                tags.append({"name": v.attribute_id.name})

            vals = {
                "name": name,
                "type": "simple",
                # "regular_price": "21.99",
                "description": "",
                "short_description": "",
                "sku": rec.default_code,
                "manage_stock": "true",
                "stock_quantity": 20,
                "categories": [
                    {
                        "id": int(categ_id)
                    },
                ],
                "images": [
                    {
                        "src": rec.url_img or rec.product_tmpl_id.url_img or ''
                    },
                    {
                        "src": rec.url_img2 or ''
                    },
                    {
                        "src": rec.url_img3 or ''
                    },
                    {
                        "src": rec.url_img4 or ''
                    },
                    {
                        "src": rec.url_img5 or ''
                    },
                ],
                "tags": tags,
            }

class ResPartnerCustomize(models.Model):
    _inherit = 'res.partner'

    phone = fields.Char(string="Số điện thoại", required=True)
    roles = fields.Selection([
        ('daily1', 'Đại lý cấp 1'),
        ('daily2', 'Đại lý cấp 2'),
        ('daily3', 'Đại lý cấp 3'),
        ('customer', 'Khách hàng lẻ')
    ], string='Cấp đại lý', default='customer', required=True)
    wp_user = fields.Char(string="Tài khoản portal")
    wp_password = fields.Char(string="Mật khẩu portal")
    type_vend = fields.Boolean(string="NCC TQ")
    vend_code = fields.Char(string="Mã phiếu GH")

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

    @api.onchange('name', 'roles')
    def action_def_pricelist(self):
        if self.name:
            pl = self.env['product.pricelist']
            def_pl = pl.search([('type_pl', '=', 'main')], limit=1)
            if self.roles:
                pl = pl.search([('roles', '=', self.roles)], limit=1)
                if pl:
                    def_pl = pl
            self.property_product_pricelist = def_pl.id

    def create_acc_distributor(self):
        com_id = self.env.company
        wp_user = com_id.wp_user
        wp_pass = com_id.wp_pass
        c = string.ascii_lowercase + string.ascii_uppercase + string.digits
        username = ''
        password = ''

        if (com_id.wp_url or wp_user or wp_pass):
            wp_url = com_id.wp_url + '/wp-json/wp/v2/users'

            if self.phone:
                if self.email:
                    email = self.email
                else:
                    email = self.phone + '@khoakim.com.vn'
                username = str(self.phone)[0:6] + random.choice(c)
                password = str(self.phone) + random.choice(c)

            if self.roles:
                data = {
                    "username": username,
                    "password": password,
                    "name": self.name,
                    "email": email,
                    "roles": self.roles,
                }
                r = requests.post(wp_url, auth=(wp_user, wp_pass), json=data)
                if (r.status_code == '201'):
                    self.write({
                        'wp_user': username,
                        'wp_password': password,
                    })
                    return {
                        'warning': {
                            'title': ('Tạo tài khoản thành công'),
                            'message': (("Tài khoản của khách hàng đã được tạo thành công! Với tên tài khoản là %s và mật khẩu là %s") % (username, password))
                        },
                    }
                else:
                    return {
                        'warning': {
                            'title': ('Đã có lỗi'),
                            'message': (("Đã có lỗi %s . Liên hệ với admin để giải đáp!") % (r.status_code)),
                        },
                    }
            else:
                return {
                    'warning': {
                        'title': ('Đã có lỗi'),
                        'message': (("Chưa cập nhật chính sách đại lý cho khách hàng này!")),
                    }
                }
        return UserError('Lỗi chưa có thông tin về website Đại lý. Hãy vào công ty để khai báo!')

    # def reset_wp_password(self):
    #     com_id = self.env.company
    #     wp_user = com_id.wp_user
    #     wp_pass = com_id.wp_pass
    #
    #     if (com_id.wp_url or wp_user or wp_pass):
    #         wp_url = com_id.wp_url + '/wp-json/wp/v2/users'

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vend_name = fields.Char(string='Mã phiếu TQ')

    @api.model
    def create(self, vals):
        partner_id = vals["partner_id"]
        name_vend = self._compute_vendor_purchase(partner_id)
        print(name_vend)
        if name_vend:
            vals['vend_name'] = name_vend
        rec = super(PurchaseOrder, self).create(vals)
        return rec

    # tính seq cho phiếu mua cùng vendor
    def _compute_vendor_purchase(self, p_id):
        partner_id = self.env['res.partner'].search([('id', '=', p_id)])
        if partner_id.type_vend and partner_id.vend_code:
            vend_code = partner_id.vend_code
            po = self.env['purchase.order']
            num_po = po.search_count([('partner_id', '=', partner_id.id)]) + 1
            name = vend_code + self.compute_seq(num_po)
            return name
        else:
            return False

    #tính seq cho phiếu mua cùng vendor
    def compute_seq(self, num_po):
        MAX_LEN = 6
        str_num = str(num_po)
        l_str = MAX_LEN - len(str_num)
        if l_str > 0:
            name = ''
            for i in range(l_str):
                name += '0'
            name += str_num
        else:
            name = False
        return name


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    prod_image = fields.Binary(string="Ảnh sản phẩm", related="product_id.image_1920")
    declare_ok = fields.Selection([
        ('no', 'Không (不)'),
        ('yes', 'Có (有)'),
    ],
        string="KBHQ", default='no')
    brand = fields.Char(string="Hãng", compute='onchange_attrs_prod')
    color = fields.Char(string="Màu", compute='onchange_attrs_prod')
    note = fields.Text(string="Ghi chú")

    @api.depends('product_id.product_template_attribute_value_ids')
    def onchange_attrs_prod(self):
        for line in self:
            brand = ''
            color = ''
            if line.product_id:
                # print(line.product_id)
                attrs = line.product_id.product_template_attribute_value_ids
                if attrs:
                    # print(attrs)
                    for a in attrs:
                        if a.attribute_id.sequence == 0:
                            brand = a.name
                        if a.attribute_id.sequence == 1:
                            color = a.name
                else:
                    brand = 'Không có'
                    color = 'Không có'
            line.brand = brand
            line.color = color

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_due = fields.Monetary(string="Công nợ hiện tại", related="partner_id.total_due")
    state = fields.Selection(selection=[
        ('draft', 'Báo giá'),
        ('waiting', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('sent', 'Đã gửi'),
        ('sale', 'Đơn hàng'),
        ('done', 'Đã khóa'),
        ('cancel', 'Đã hủy'),
    ], string='Trạng thái', readonly=True, copy=False, index=True, track_visibility='onchange',
        track_sequence=3, default='draft')
    sm_signture = fields.Binary(string="Chữ ký NVKD", related="user_id.sign_signature")
    pst_by_word = fields.Char(string="Số tiền bằng chữ", compute='_compute_subtotal_word')

    @api.depends('amount_total')
    def _compute_subtotal_word(self):
        if self.amount_total:
            pst_word = n2w(str(self.amount_total/10))
            self.pst_by_word = pst_word.capitalize() + ' đồng'
        else:
            self.pst_by_word = ''

    #tạo hoá đơn
    def customize_sale_confirm(self):
        self.action_confirm()
        return {
            'name': _('Ghi nhận thanh toán'),
            'res_model': 'sale.order.invoice.kk',
            'view_mode': 'form',
            'context': {
                'active_model': 'sale.order',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    #kiem tra quyen duyet
    def check_pass_perm(self):
        group_pass = 'khoakim_customize.group_pass_approval_sale_order'
        user_id = self.env.user
        if user_id.has_group(group_pass):
            return True
        return False

    #kiem tra gia tien bao gia
    def check_price_quotation(self):
        if self.order_line:
            for line in self.order_line:
                if line.price_unit == 0:
                    return line.name
        return False

    #check có chiet khau
    def check_discount(self):
        for l in self.order_line:
            discount = l.discount or l.cus_discount
            if discount > 0.0:
                return l.product_id.name
        return False

    #xét duyệt báo giá
    def action_quotation_approval(self):
        check_price = self.check_price_quotation()
        if check_price:
            raise UserError(("Vui lòng kiểm tra lại sản phẩm %s chưa có giá tiền") % (check_price))

        check_perm_pass = self.check_pass_perm()
        # iv = False
        if self.state in ['draft', 'waiting', 'sent']:
            if check_perm_pass == False:
                disc = self.check_discount()
                if disc:
                    self.write({'state': 'waiting'})
                    self.notify_manager()
                    return {
                                'warning': {
                                                'title': ('Hãy chờ chút'),
                                                'message': (("Do sản phẩm %s đang được chiết khấu nên cần phải duyệt! Vui lòng thông báo tới khách hàng") % (disc)),
                                            },
                            }
        return {
            'name': _('Ghi nhận thanh toán'),
            'res_model': 'sale.order.invoice.kk',
            'view_mode': 'form',
            'context': {
                'active_model': 'sale.order',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

        # iv = self.customize_sale_confirm()

        # if iv:
        #     return iv.action_register_payment()
        # else:
        #     return {
        #         'warning': {
        #                         'title': ('Kiểm tra lại cấu hình sản phẩm'),
        #                         'message': ("Không thể tạo hóa đơn theo đơn hàng"),
        #                     },
        #     }

    #xác nhận báo giá
    def action_accept_approval(self):
        # iv = self.customize_sale_confirm()
        # if iv:
        #     return iv.action_register_payment()
        # else:
        #     return {
        #         'warning': {
        #                         'title': ('Kiểm tra lại cấu hình sản phẩm'),
        #                         'message': ("Không thể tạo hóa đơn theo đơn hàng"),
        #                     },
        #     }
        self.write({'state': 'approved'})
        self.notify_manager()

    def action_deny_approval(self):
        self.write({'state': 'draft'})

    def notify_manager(self):
        if self.state == 'waiting':
            manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).parent_id
            if manager:
                for sale_approval in self.filtered(lambda hol: hol.state == 'waiting'):
                    # print(sale_approval)
                    sale_approval.activity_schedule(
                        'khoakim_customize.mail_act_sale_approval_kk',
                        user_id=manager.user_id.id or self.env.uid)
            else:
                return {
                        'warning': {
                            'title': ('Đã có lỗi'),
                            'message': (("Chưa tìm được người duyệt, vui lòng liên hệ admin!")),
                        },
                    }

        self.filtered(lambda hol: hol.state in ['sale', 'approved', 'done']).activity_feedback(
            ['khoakim_customize.mail_act_sale_approval_kk'])
        self.filtered(lambda hol: hol.state in ['draft', 'cancel']).activity_unlink(
            ['khoakim_customize.mail_act_sale_approval_kk'])
        if self.state == 'draft':
            for sale_deny in self.filtered(lambda hol: hol.state == 'draft'):
                # print(sale_approval)
                sale_deny.activity_schedule(
                    'khoakim_customize.mail_act_sale_approval_kk',
                    user_id=sale_deny.user_id.id or self.env.uid)

    #thông báo khi cập nhật đơn hàng
    def notify_so_mess(self):
        if self.state:
            channel_all = self.env['mail.channel'].search([('id', '=', 1)])
            vals = {
                'message_type': 'comment',
                'subtype_id': self.env.ref('mail.mt_note').id,
                'model': 'mail.channel',
                'res_id': channel_all.id,
                'body': "Test đơn hàng",
            }
            mess = self.env['mail.message'].create(vals)
            print(mess)
            return mess

    #cập nhật giá sản phẩm
    def update_prices_custom(self):
        self.ensure_one()
        for line in self.order_line.filtered(lambda line: not line.display_type):
            line.new_price_unit = 0.0
            line.product_uom_change()
            line.discount = 0  # Force 0 as discount for the cases when _onchange_discount directly returns
            line._onchange_discount()
            line.new_price_unit = line.price_unit

        self.show_update_pricelist = False
        self.message_post(body=_("Giá của sản phẩm đã được cập nhật theo bảng giá <b>%s<b> ", self.pricelist_id.display_name))


class ResCompanyAccountLine(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'res.company.account.lines'
    _rec_name = 'name'
    _description = 'Thông tin tài khoản'

    company_id = fields.Many2one('res.company', string='Công ty')
    name = fields.Char(string='Tài khoản', compute='_compute_name')
    type = fields.Selection([
                                ('person', 'Cá nhân'),
                                ('company', 'Công ty'),
                            ], string= 'Loại tài khoản', default='person', require=True)
    acc_holder = fields.Char(string='Tên tài khoản', require=True)
    acc_number = fields.Char(string='Số tài khoản', require=True)
    bank_id = fields.Many2one('res.bank', string="Ngân hàng", require=True)
    branch = fields.Char(string='Chi nhánh')
    qr_code = fields.Binary(string='Mã QR code')

    @api.depends('acc_number', 'bank_id.name')
    def _compute_name(self):
        for line in self:
            if line.bank_id.name and line.acc_number:
                line.name = line.acc_number + ' - ' + line.bank_id.name
            else:
                line.name = ''

class ResCompanyCustomize(models.Model):
    _inherit = 'res.company'

    wp_url = fields.Char(string='Link website')
    wp_user = fields.Char(string='Tài khoản WP')
    wp_pass = fields.Char(string='Mật khẩu WP')
    woo_ck = fields.Char(string='Keys Woocommerce')
    woo_cs = fields.Char(string='Secret Woocommerce')
    sign_company = fields.Binary(string='Dấu công ty')
    account_lines = fields.One2many('res.company.account.lines', 'company_id',
                                    string='Tài khoản ngân hàng')

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_check_out_wh(self):
        if self.picking_type_code == 'outgoing':
            if self.move_ids_without_package:
                for line in self.move_ids_without_package:
                    prod = line.product_id
                    if (prod.weight == False or prod.volumn == False ):
                        raise UserError(("Vui lòng kiểm tra lại sản phẩm %s chưa có khối lượng hoặc thể tích") % (prod.name))
        self.action_confirm()

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    prod_image = fields.Binary(string="Ảnh sản phẩm", related="product_id.image_1920")

class StockMove(models.Model):
    _inherit = 'stock.move'

    prod_image = fields.Binary(string="Ảnh sản phẩm", related="product_id.image_1920")

# class WPSetting(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     wp_url = fields.Char(string='URL website')
#     wp_user = fields.Char(string='Tài khoản WP')
#     wp_pass = fields.Char(string='Mật khẩu WP')
#     woo_ck = fields.Char(string='Keys Woocommerce')
#     woo_cs = fields.Char(string='Secret Woocommerce')