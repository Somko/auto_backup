from backupstore import BackupStore


class SambaStore(BackupStore):
    def upload(self, local_file, remote_location):
        pass

    def cleanup(self, days):
        pass
