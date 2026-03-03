{
    'name': 'Web HTML Extender',
    'version': '16.0.1.0.0',
    'depends': ['base', 'web', 'web_editor', 'mail'],
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            'web_html_extender/static/src/js/html_canned_response.js',
        ],
        # Only needed If creating new widget
        # 'web_editor.assets_wysiwyg': [
        #     'web_html_extender/static/src/js/wysiwyg.js',
        # ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
