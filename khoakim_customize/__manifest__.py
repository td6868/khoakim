# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Khoa Kim Customize',
    'version' : '1.1',
    'summary': 'Invoices & Payments',
    'sequence': 115,
    'description': """
            Module tổng hợp các tùy biến Khoa Kim ERP
    """,
    'category': 'Customize',
    'website': 'https://www.odoo.com/page/billing',
    'data': [
        'views/inherit_views.xml',
    ],
    "depends": [
        "sale",
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
}
