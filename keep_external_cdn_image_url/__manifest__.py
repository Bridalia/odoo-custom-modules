# -*- coding: utf-8 -*-
{
    'name': 'Keep External CDN Image url',
    'summary': """
        Using upload media by External URL, the media will be upload to Odoo then replace by Internal URL""",
    'description': """Keep Origin Image URL""",
    'category': 'Website/Tools',
    'version': '17.0.1.0.1',
    'author': 'Jason Vu',
    'email': "longvm91@gmail.com",
    'website': "https://github.com/longvm91/odoo-custom-modules/tree/17.0/keep_external_cdn_image_url",
    'module_type': 'official',
    'depends': ['web_editor'],
    'data': [
    ],
    'assets': {
        'web_editor.assets_media_dialog': [
            'keep_external_cdn_image_url/static/src/components/media_dialog/web_editor.js',
            'keep_external_cdn_image_url/static/src/components/media_dialog/*.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
