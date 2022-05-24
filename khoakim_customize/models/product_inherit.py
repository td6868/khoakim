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

class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    type_pl = fields.Selection([
        ('main', 'Bảng giá niêm yết'),
        ('policy', 'Theo chính sách'),
        ('non_policy', 'Không theo chính sách')
    ], string="Loại bảng giá", default='main', required=True)
    def_pl_id = fields.Many2one('product.pricelist',string="Bảng giá NY", domain=[('type_pl', '=', 'main')])
    discount = fields.Float(string='Chiết khấu theo bảng giá (%)', tracking=True)
    type_dics = fields.Selection([
        ('perc', 'Phần trăm'),
        ('fix', 'Tiền cố định')
    ], string='Loại chiết khấu')
    catg_id = fields.Many2one('product.category',string='Danh mục SP', tracking=True, onchange=True)
    catg_disc = fields.Float(string='Chiết khấu', tracking=True)
    roles = fields.Selection([
        ('daily1', 'Đại lý cấp 1'),
        ('daily2', 'Đại lý cấp 2'),
        ('daily3', 'Đại lý cấp 3'),
        ('customer', 'Khách hàng lẻ')
    ], string='Cấp đại lý', default='customer', required=True)

    # def write(self, vals):
    #     super(Pricelist, self).write(vals)

    def action_price_categ(self):
        if self.catg_id and self.catg_disc and self.type_dics:
            for l in self.item_ids:
                categ_ids = self.env['product.category'].search([('id', 'child_of', [self.catg_id.id])])
                for cid in categ_ids:
                    if l.product_tmpl_id.categ_id.id == cid.id:
                        cur_price = l.fixed_price
                        if self.type_dics == 'perc':
                            l.fixed_price = ((100.00 - self.catg_disc) / 100.00) * cur_price
                        elif self.type_dics == 'fix':
                            l.fixed_price = cur_price - self.catg_disc
            self.write({
                'catg_id': False,
                'type_dics': False,
                'catg_disc': False
            })

    def _update_price_policy(self):
        if self.discount:
            for l in self.item_ids:
                cur_price = l.fixed_price
                l.fixed_price = ((100.00 - self.discount) / 100.00) * cur_price

    def action_update_main_price(self):
        pl = self.env['product.pricelist']
        pl_ids = pl.search([('def_pl_id', '=', self.id)])
        pl_item_ids = []
        pl_update = ''
        for item in self.item_ids:
            pl_item_ids.append((0, item.id,
                                {
                                    'product_tmpl_id': item.product_tmpl_id.id,
                                    'product_id': item.product_id.id,
                                    'min_quantity': item.min_quantity,
                                    'fixed_price': ((100.00 - self.discount) / 100.00) * item.fixed_price,
                                    'date_start': item.date_start,
                                    'date_end': item.date_end
                                }))
        for pl_id in pl_ids:
            if pl_id.item_ids:
                for i in pl_id.item_ids:
                    i.unlink()
            pl_id.write({
                'item_ids': pl_item_ids,
                })
            pl_id._update_price_policy()
            pl_update += str(pl_id.name) + ', '
        return {
                        'warning': {
                            'title': ('Đã hoàn thành'),
                            'message': (("Đã cập nhật các bảng giá sau %s") % (pl_update))
                        },
                    }

    def action_update_price(self):
            pl_item_ids = []
            for item in self.def_pl_id.item_ids:
                pl_item_ids.append((0, item.id,
                {
                    'product_tmpl_id': item.product_tmpl_id.id,
                    'product_id': item.product_id.id,
                    'min_quantity': item.min_quantity,
                    'fixed_price': ((100.00 - self.discount) / 100.00) * item.fixed_price ,
                    'date_start': item.date_start,
                    'date_end': item.date_end
                }))
            if self.item_ids:
                for i in self.item_ids:
                    i.unlink()
            self.write({
                'item_ids': pl_item_ids,
            })

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    prod_image = fields.Binary(string="Ảnh sản phẩm", related="product_id.image_1920")
    qty_available = fields.Float(string="Tồn kho", related="product_id.qty_available")
    cus_discount = fields.Float(string='CK ($)')

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

    @api.depends("product_uom_qty", "discount", "price_unit", "tax_id", "cus_discount")
    def _compute_amount(self):
        vals = {}
        for line in self.filtered(
                lambda l: l.cus_discount and l.order_id.state not in ["done", "cancel"]
        ):
            real_price = line.price_unit * (1 - (line.discount or 0.0) / 100.0) - (
                    line.cus_discount or 0.0
            )
            twicked_price = real_price / (1 - (line.discount or 0.0) / 100.0)
            vals[line] = {
                "price_unit": line.price_unit,
            }
            line.update({"price_unit": twicked_price})
        res = super(SaleOrderLine, self)._compute_amount()
        for line in vals.keys():
            line.update(vals[line])
        return res

class AccountMove(models.Model):
    _inherit = "account.move"

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

    cus_discount = fields.Float(string='CK ($)')

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
        balance,
        move_type,
        currency,
        taxes,
        price_subtotal,
        force_computation=False,
    ):
        if self.cus_discount != 0:
            discount = ((self.cus_discount) / self.price_unit) * 100 or 0.00
        return super(AccountMoveLine, self)._get_fields_onchange_balance_model(
            quantity,
            discount,
            balance,
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
    prod_code = fields.Char(string="Mã SP/NSX", required=True)

    # @api.model
    # def create(self, vals):
    #     rec = super(ProductTemplate, self).create(vals)
    #     if self.wp_ok == True:
    #         self.update_product_wp()
    #     return rec

    # def write(self, vals):
    #     super(ProductTemplate, self).write(vals)
    #     if self.wp_ok == True:
    #         self.update_product_wp()

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
            get_img = urllib.request.urlopen(self.url_img).read()
            img_b64 = base64.encodestring(get_img)
            self.write({
                "image_1920": img_b64,
            })

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

    def update_product_wp(self):
        com_id = self.env.company
        wp_url = com_id.wp_url
        woo_ck = com_id.woo_ck
        woo_cs = com_id.woo_cs
        sku_wp = ''

        if (wp_url == False or woo_ck == False or woo_cs == False):
            return sku_wp

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
                    "src": self.url_img or ''
                },
            ]
        }

        if self.sku_wp:
            update = wcapi.put("products/" + str(self.sku_wp), data)
        else:
            update = wcapi.post("products", data)

        status = update.status_code
        js = update.json()

        if status == 201:
            js = update.json()
            self.write({
                'sku_wp': js['id']
            })

        print(js['id'])
        print(status)

    @api.model
    def sync_product_wp(self):
        com_id = self.env['res.company'].search([('id', '=', 1)])
        wp_url = com_id.wp_url
        woo_ck = com_id.woo_ck
        woo_cs = com_id.woo_cs
        sku_wp = ''

        if (wp_url == False or woo_ck == False or woo_cs == False):
            return sku_wp

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
        sku_wp = ''

        if (wp_url == False or woo_ck == False or woo_cs == False):
            return sku_wp

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
                    "regular_price": str(p.list_price),
                }
                update = wcapi.put("products/" + str(p.sku_wp), data)
                status = update.status_code
                js = update.json()
                print(js['id'])
                print(status)
            else:
                p.update_product_wp()

class ProductAttributeValues(models.Model):
    _inherit = 'product.attribute.value'

    acode = fields.Char(string='Mã biến thể', required=True)
    attr_term_wp = fields.Char(string='ID')

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    attr_wp = fields.Char(string='ID')

    def update_attrs_wp(self):
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
            "name": self.name,
            "type": "select",
            "order_by": "menu_order",
            "has_archives": True
        }

        if self.cate_id:
            update = wcapi.put("products/attributes/" + str(self.cate_id), data)
            status = update.status_code
        else:
            update = wcapi.post("products/attributes", data)
            status = update.status_code
            if status == 201:
                js = update.json()
                self.cate_id = js['id']
        print(status)

class ProductCategory(models.Model):
    _inherit = 'product.category'

    ccode = fields.Char(string="Mã nhóm sản phẩm", required=True)
    cate_code = fields.Char(string="Mã nhóm", compute='_gene_code_cate', store=True)
    cate_id = fields.Char(string="ID")
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

    def update_categ_wp(self):
        com_id = self.env.company
        wp_url = com_id.wp_url
        woo_ck = com_id.woo_ck
        woo_cs = com_id.woo_cs

        if (wp_url == False or woo_ck == False or woo_cs == False or self.wp_ok == False):
            return True

        wcapi = API(
            url=wp_url,
            consumer_key=woo_ck,
            consumer_secret=woo_cs,
            version="wc/v3",
            timeout=30
        )

        data = {
            "name": self.name,
            "parent": self.parent_id.cate_id or 0,
            "description": "",
        }

        if self.cate_id:
            update = wcapi.put("products/categories/" + str(self.cate_id), data)
            status = update.status_code
        else:
            update = wcapi.post("products/categories", data)
            status = update.status_code
            if status == 201:
                js = update.json()
                self.cate_id = js['id']
        print(status)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    prod_code = fields.Char(string="Mã SP/SX", compute='_get_temp_prod')
    default_code = fields.Char(string="Mã nội bộ", compute='_gen_product_attrs_code', store=True)

    def _get_temp_prod(self):
        for p in self:
            if p.product_tmpl_id:
                p.prod_code = p.product_tmpl_id.prod_code or ''

    @api.depends('product_template_attribute_value_ids', 'prod_code', 'product_tmpl_id.default_code')
    def _gen_product_attrs_code(self):
        for prod in self:
            code = prod.product_tmpl_id.default_code or ''
            attrs = prod.product_template_attribute_value_ids
            b = []
            for s in attrs:
                b.append((s.attribute_id.sequence, s.product_attribute_value_id.acode))
            d = sorted(b)
            for c in d:
                code += c[1] or ''
            prod.default_code = code
#             print(code)

    @api.onchange('url_img')
    def onchange_image(self):
        if self.url_img:
            get_img = urllib.request.urlopen(self.url_img).read()
            img_b64 = base64.encodestring(get_img)
            self.write({
                "image_1920": img_b64,
            })

class ResPartnerCustomize(models.Model):
    _inherit = 'res.partner'

    phone = fields.Char(string="Số điện thoại", required=True)
    roles = fields.Selection([
        ('daily1', 'Đại lý cấp 1'),
        ('daily2', 'Đại lý cấp 2'),
        ('daily3', 'Đại lý cấp 3'),
        ('customer', 'Khách hàng lẻ')
    ], string='Cấp đại lý', default='customer', required=True)

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
            if self.roles:
                def_pl = pl.search([('roles', '=', self.roles)], limit=1)
            else:
                def_pl = pl.search([('type_pl', '=', 'main')])
            self.propety_product_pricelist = def_pl.id

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
                username = str(self.phone)[0:6]
                password = str(self.phone)
                data = {
                    "username": str(self.phone)[0:7],
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
        group_pass = 'khoakim_customize.group_pass_approval_sale_order'
        user = self.env.user
        if user.has_group(group_pass):
            self.customize_sale_confirm()
        else:
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
