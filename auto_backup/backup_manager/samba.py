import os

import datetime
from odoo import tools

from backupstore import BackupStore
from smb.SMBConnection import SMBConnection


class SambaStore(BackupStore):
    def upload(self, local_file, remote_location):
        conn = self._get_conn()
        self._create_dir(conn, remote_location)
        with open(local_file, 'rb') as file:
            conn.storeFile(self.obj.samba_name, remote_location + "/" + local_file.split("/")[-1], file)
        conn.close()

    def cleanup(self, remote_path, days):
        conn = self._get_conn()
        for file in conn.listPath(self.obj.samba_name, remote_path):
            # Get the full path
            fullpath = os.path.join(remote_path, file.filename)
            # Get the timestamp from the file on the external server
            timestamp = file.create_time
            createtime = datetime.datetime.fromtimestamp(timestamp)
            now = datetime.datetime.now()
            delta = now - createtime
            # If the file is older than the days_to_keep_sftp (the days to keep that the user filled in on the Odoo form it will be removed.
            if delta.days >= days:
                # Only delete files, no directories!
                if not file.isDirectory and (".dump" in file.filename or '.zip' in file.filename):
                    print "Delete too old file from server: " + file.filename
                    conn.deleteFiles(self.obj.samba_name, fullpath)
        conn.close()

    def test(self):
        conn = self._get_conn()
        message_title = "Connection Test Succeeded!"
        message_content = "Everything seems properly set up for Windows Share back-ups!"
        try:
            conn.listPath(self.obj.samba_name, "/", timeout=30)
        except Exception, e:
            message_title = "Connection Test Failed!"
            message_content = "Here is what we got instead:\n" + tools.ustr(e)
        return message_title, message_content

    def _get_conn(self):
        conn = SMBConnection(self.obj.user, self.obj.password, "odoo",
                             self.obj.samba_domain, use_ntlm_v2=True, is_direct_tcp=True)
        conn.connect(self.obj.host, self.obj.samba_port)
        return conn

    def _create_dir(self, conn, dir):
        current_path = ""
        for sub_dir in dir.replace("\\", "/").split("/"):
            if sub_dir not in conn.listPath(self.obj.samba_name, current_path):
                if current_path != "":
                    conn.createDirectory(self.obj.samba_name, current_path)
                current_path += sub_dir + "/"
