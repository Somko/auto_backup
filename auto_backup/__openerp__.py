# -*- encoding: utf-8 -*-
{
    'name' : 'Database Auto-Backup',
    'version' : '10.0',
    'author' : 'Somko',
    'website' : 'https://somko.be/',
    'category' : 'Generic Modules',
    'summary': 'Backups',
    'description': "",
    'depends' : ['base'],
    'data': [
      'views/bkp_conf_view.xml',
      'data/backup_data.xml',
    ],
    'auto_install': False,
    'installable': True
}
