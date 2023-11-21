import os
import paramiko

class SSHConnection(object):
    def __init__(self, host, port, user, password=None, private_key_path=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.private_key_path = private_key_path
        assert self.password or self.private_key_path

        self._createSSHClient()

    def _createSSHClient(self):
        # SSH + cat is not encrypted
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.password is not None:
            client.connect(self.host, self.port, self.user, self.password)
        else:
            private_key = paramiko.RSAKey(filename=self.private_key_path)
            client.connect(self.host, self.port, self.user, pkey=private_key)
        self.client = client
        print(f'Connected to', self.host, '...')
    
    def _createSFTPClient(self):
        # TODO: SFTP not used now, may be used in the future for security
        client = paramiko.Transport((self.host, self.port))
        client.connect(username=self.user, password=self.password)
        self.client = client

    def check_path_exists(self, path):
        command = f'ls {path}'
        stdin, stdout, stderr = self.client.exec_command(command)
        return bool(stderr.read())

    def get_remote_file_content(self, filename):
        '''
        Args:
            filename: remote file path
        Return: bytes file content
        '''
        command = f'cat {filename}'
        stdin, stdout, stderr = self.client.exec_command(command)
        file_bytes = stdout.read() # file bytes
        return file_bytes

    def getAllFiles(self, folder, suffix=('.png', '.jpg', '.jpeg'), full_path=False):
        if isinstance(suffix, str):
            suffix = (suffix)
        cmd_suffix = f' {folder}/*'.join(suffix)
        cmd = f'ls {folder}/*{cmd_suffix}'
        
        stdin, stdout, stderr = self.client.exec_command(cmd)
        file_list = stdout.read().decode('utf-8').split('\n')
        # remove all empty string
        file_list = [s.strip() for s in file_list if s.strip()]
        if full_path:
            return file_list
        return [os.path.basename(f) for f in file_list]

    def __del__(self):
        self.client.close()