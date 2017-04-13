import os

import datetime

from backupstore import BackupStore
import pysftp
from odoo import tools


cnopts = pysftp.CnOpts()
cnopts.hostkeys = None


class SftpStore(BackupStore):
    def upload(self, local_file, remote_path):
        srv = self._get_srv()
        self._mkdir_p(srv, remote_path)
        srv.put(local_file)
        srv.close()

    def cleanup(self, remote_path, days):
        srv = self._get_srv()
        srv.chdir(remote_path)
        for file in srv.listdir(remote_path):
            # Get the full path
            fullpath = os.path.join(remote_path, file)
            # Get the timestamp from the file on the external server
            timestamp = srv.stat(fullpath).st_atime
            createtime = datetime.datetime.fromtimestamp(timestamp)
            now = datetime.datetime.now()
            delta = now - createtime
            # If the file is older than the days_to_keep_sftp (the days to keep that the user filled in on the Odoo form it will be removed.
            if delta.days >= days:
                # Only delete files, no directories!
                if srv.isfile(fullpath) and (".dump" in file or '.zip' in file):
                    print "Delete too old file from SFTP servers: " + file
                    srv.unlink(file)
        srv.close()

    def test(self):
        message_content = ""
        try:
            # Connect with external server over SFTP, so we know sure that everything works.
            srv = self._get_srv()
            srv.close()
            # We have a success.
            message_title = "Connection Test Succeeded!"
            message_content = "Everything seems properly set up for FTP back-ups!"
        except Exception, e:
            message_title = "Connection Test Failed!"
            if len(self.obj.host) < 8:
                message_content += "\nYour IP address seems to be too short.\n"
            message_content += "Here is what we got instead:\n" + tools.ustr(e)
        return message_title, message_content

    def _get_srv(self):
        srv = pysftp.Connection(host=self.obj.host, username=self.obj.user, password=self.obj.password,
                                port=self.obj.port, cnopts=cnopts)
        srv._transport.set_keepalive(30)
        return srv

    def _mkdir_p(self, srv, remote_directory):
        """Change to this directory, recursively making new folders if needed.
        Returns True if any folders were created."""
        if remote_directory == '/':
            # absolute path so change directory to root
            srv.chdir('/')
            return
        if remote_directory == '':
            # top-level relative directory must exist
            return
        try:
            srv.chdir(remote_directory)  # sub-directory exists
        except IOError:
            dirname, basename = os.path.split(remote_directory.rstrip('/'))
            self._mkdir_p(srv, dirname)  # make parent directories
            srv.mkdir(basename)  # sub-directory missing, so created it
            srv.chdir(basename)
            return True
