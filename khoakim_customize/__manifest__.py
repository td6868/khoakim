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
        'security/security.xml',
        'views/inherit_views.xml',
        'data/data.xml',
        'data/mail_data.xml',
    ],
    "depends": [
        "sale",
        "base",
        "product",
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
}
