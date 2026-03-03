# -*- coding: utf-8 -*-

{
    'name' : 'Attachment Previewer',
    'version' : '18.0.1.0.0',
    'summary': 'Attachment Previewer',
    'sequence': 13,
    'description': """
		Added functionality that will enable preview in kanban mode as well
    """,
    'category': 'web',
    'depends': ['web', 'mail'],
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            "web_attachment_previewer/static/src/js/attachment_preview.js",
            "web_attachment_previewer/static/src/js/kanban_renderer.js",
            "web_attachment_previewer/static/src/js/many2many_binary_field.js",
            "web_attachment_previewer/static/src/xml/mail_attachment.xml",
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
