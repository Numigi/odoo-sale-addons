# -*- coding: utf-8 -*-
{
    'name': 'Contacts Maps',
    'version': '14.0.1.0.0',
    'author': 'Yopi Angi',
    'license': 'AGPL-3',
    'maintainer': 'Yopi Angi<yopiangi@gmail.com>',
    'support': 'yopiangi@gmail.com',
    'category': 'Tools',
    'description': """
Contacts Maps
=============

Added map view on contacts
""",
    'depends': [
        'contacts',
        'base_geolocalize',
        'web_google_maps',
        'google_marker_icon_picker'
    ],
    'website': '',
    'data': [
        'views/res_partner.xml',
    ],
    'demo': [],
    'installable': True
}
