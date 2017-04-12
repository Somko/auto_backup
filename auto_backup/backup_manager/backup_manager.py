import functools
import os
import shutil
import time

import requests
from odoo import tools

from local import LocalStore
from samba import SambaStore
from sftp import SftpStore

tmp_folder = "/tmp/odoo/auto_backup"
odoo_port = tools.config['xmlrpc_port']
odoo_host = "localhost" if tools.config['xmlrpc_interface'] == '' else tools.config['xmlrpc_interface']


class BackupManager:

    def __init__(self, obj):
        self.obj = obj
        self.db = obj._cr.dbname
        self.folder = tmp_folder + "/" + str(self.obj.id)

    def backup_db(self):
        self._get_backup_file()
        store = self._get_store()
        for f in os.listdir(self.folder):
            fullpath = os.path.join(self.folder, f)
            if os.path.isfile(fullpath):
                store.upload(fullpath, self.obj.remote_path)
                os.remove(fullpath)
        if self.obj.autoremove and self.obj.days_to_keep > 0:
            store.cleanup(self.obj.remote_path, self.obj.days_to_keep)

    def _get_store(self):
        if self.obj.store_type == "sftp":
            return SftpStore(self.obj)

    def _get_backup_file(self):
        try:
            if not os.path.isdir(self.folder):
                os.makedirs(self.folder)
        except:
            raise
        # Create name for dumpfile.
        bkp_file = '%s_%s.%s' % (time.strftime('%d_%m_%Y_%H_%M_%S'),  self.db, self.obj.backup_type)
        file_path = os.path.join(self.folder, bkp_file)
        uri = 'http://' + odoo_host + ':' + str(odoo_port)
        try:
            bkp_resp = requests.post(
                uri + '/web/database/backup', stream=True,
                data={
                    'master_pwd': tools.config['admin_passwd'],
                    'name': self.db,
                    'backup_format': self.obj.backup_type
                }
            )
            bkp_resp.raise_for_status()
        except:
            print "Couldn't backup database %s. Bad database administrator password for server running at http://%s:%s"
            return False
        with open(file_path, 'wb') as fp:
            # see https://github.com/kennethreitz/requests/issues/2155
            bkp_resp.raw.read = functools.partial(
                bkp_resp.raw.read, decode_content=True)
            shutil.copyfileobj(bkp_resp.raw, fp)
        return file_path
