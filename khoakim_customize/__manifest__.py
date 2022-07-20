# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Khoa Kim Customize',
    'version' : '1.1',
    'summary': 'Invoices & Payments',
    'sequence': 115,
    "license": "AGPL-3",
    'description': """
            Module tổng hợp các tùy biến Khoa Kim ERP
    """,
    'category': 'Customize',
    'website': 'https://www.odoo.com/page/billing',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/mail_data.xml',
        'report/sale_order_rp.xml',
        'report/invoice_rp.xml',
        'report/stock_picking_rp.xml',
        'report/purchase_order_rp.xml',
        'report/customize_report.xml',
        'views/inherit_views.xml',
        'wizard/invoice_so.xml',
        'data/data.xml',
    ],
    "depends": [
        "sale",
        "base",
        "product",
        "report_xlsx",
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
}
