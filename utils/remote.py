import paramiko

# from .config.

class SSHConnection(object):
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

        # self._createSSHClient()
        # self._createSFTPClient()

    def createSSHClient(self):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy)
        client.connect(self.host, self.port, self.user, self.password)
        self.client = client
    
    def createSFTPClient(self):
        client = paramiko.Transport((self.host, self.port))
        client.connect(username=self.user, password=self.password)
        self.client = client

    def sftpListDir(self, remoteDir, localDir):
        sftp = self.client.open_sftp()
        files = sftp.listdir(path=remoteDir)
        sftp.close()
        return files
        for f in files:
            print('Retrieving', f)
            sftp.get(remoteDir + f, localDir + f)

    def __del__(self):
        self.client.close()