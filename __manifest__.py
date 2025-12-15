# -*- coding: utf-8 -*-
{
    'name': "Gestion Location Vélos",
    'summary': "Vente et Location de vélos",
    'description': """Module pour gérer un magasin de vélos""",
    'author': "Léo",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['base', 'sale', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/bike_views.xml',
        'views/bike_menus.xml',
        # 'reports/rental_report.xml',
    ],
    'application': True,
}