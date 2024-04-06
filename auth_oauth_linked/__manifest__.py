# Copyright 2024 Jason Vu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Linked Multi OAuths",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Jason Vu",
    'email': "longvm91@gmail.com",
    'website': "https://github.com/longvm91/odoo-custom-modules/tree/17.0/auth_oauth_linked",
    "summary": """Allow linked multiple OAuths to account""",
    "category": "Tool",
    "website": "",
    "depends": ["auth_oauth","portal"],
    "data": [
        'security/ir.model.access.csv',
        'views/linked_oauth_templates.xml',
        'views/res_config_settings_views.xml',
    ],
    'images': ['static/img/allow_unlink.png'],
    'assets': {
        'web.assets_frontend': [
            'auth_oauth_linked/static/src/**/*',
        ],
    },
    "installable": True,
}
