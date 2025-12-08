{
    'name': 'Rental Management',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Manage rental orders with invoicing',
    'description': """
        Rental Management Module
        ========================
        * Create rental orders with start and end dates
        * Automatic price calculation
        * Invoice generation
        * Status management (draft, confirmed, in progress, done, cancelled)
    """,
    'author': 'Your Company',
    'data': [
        'security/ir.model.access.csv',
        'views/rental_order_views.xml',
        'views/rental_menu.xml',        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}