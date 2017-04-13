import os

import datetime

from backupstore import BackupStore


class LocalStore(BackupStore):
    def upload(self, local_file, remote_location):
        os.rename(local_file, remote_location + "/" + local_file.split("/")[-1])

    def cleanup(self, remote_path, days):
        for f in os.listdir(remote_path):
            fullpath = os.path.join(dir, f)
            timestamp = os.stat(fullpath).st_ctime
            createtime = datetime.datetime.fromtimestamp(timestamp)
            now = datetime.datetime.now()
            delta = now - createtime
            if delta.days >= days:
                # Only delete files (which are .dump and .zip), no directories.
                if os.path.isfile(fullpath) and (".dump" in f or '.zip' in f):
                    print  "Delete local out-of-date file: " + fullpath
                    os.remove(fullpath)

    def test(self):
        if not os.path.isdir(self.obj.remote_path):
            try:
                os.mkdir(self.obj.remote_path)
            except Exception:
                return "Connection Test Failed!", "We cannot create that folder!"
        if os.access(self.obj.remote_path, os.W_OK):
            return "Connection Test Succeeded!", "We have permissions to write in that folder!"
        else:
            return "Connection Test Failed!", "We do not have permissions to write in that folder!"
