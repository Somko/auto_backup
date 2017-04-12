class BackupStore:
    def __init__(self, obj):
        self.obj = obj

    def upload(self, local_file, remote_location):
        pass

    def cleanup(self, remote_path, days):
        pass

    def test(self):
        pass
