# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, tools, _
from odoo.exceptions import Warning

from auto_backup.backup_manager import BackupManager
from auto_backup.backup_manager.backup_manager import possible_stores


class db_backup(models.Model):
    _name = 'db.backup'

    # Columns for local server configuration
    name = fields.Char(required=True, default="backup")
    backup_type = fields.Selection([('zip', 'Zip'), ('dump', 'Dump')], 'Backup Type', required=True, default='zip')
    store_type = fields.Selection(possible_stores.values(), default="local", required=True)
    autoremove = fields.Boolean('Auto. Remove Backups', help='If you check this option you can choose to automaticly remove the backup after xx days')

    #common fields
    remote_path = fields.Char()
    days_to_keep = fields.Integer('Remove after x days',
                                  help="Choose after how many days the backup should be deleted. For example:\nIf you fill in 5 the backups will be removed after 5 days.",
                                  required=True)
    host = fields.Char('IP Address Server', help='The IP address from your remote server. For example 192.168.0.1')
    user = fields.Char('Username Server', help='The username where the connection should be made with. This is the user on the external server.')
    password = fields.Char('Password User Server',
                           help='The password from the user where the connection should be made with. This is the password from the user on the external server.')

    sftp_port = fields.Integer('Port', help='The port on the server that accepts SSH/SFTP calls.', default=22)

    samba_domain = fields.Char("Domain/Workgroup", default="WORKGROUP")
    samba_name = fields.Char("Share name")
    samba_port = fields.Integer("port", default=445)

    @api.multi
    def test_connection(self):
        self.ensure_one()
        message_title, message_content = BackupManager(self).get_store().test()
        raise Warning(_(message_title + '\n\n' + message_content))

    @api.multi
    def test_backup(self):
        self.ensure_one()
        try:
            BackupManager(self).backup_db()
        except Exception, e:
            raise Warning(_("Something went terribly wrong: " + tools.ustr(e)))
        raise Warning(_("Backup seems to have worked, up to you to validate!"))

    @api.multi
    def schedule_backup(self):
        conf_ids = self.search([])
        for conf in conf_ids:
            BackupManager(conf).backup_db()
