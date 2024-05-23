import os
import paramiko

DEFAULT_SSH_CONFIG_PATH = '~/.ssh/config'
DEFAULT_KEY_PATH = '~/.ssh/id_rsa'

def load_ssh_config(ssh_cfg_path=DEFAULT_SSH_CONFIG_PATH):
    config_path = os.path.expanduser(ssh_cfg_path)
    ssh_config = paramiko.SSHConfig()
    with open(config_path) as f:
        ssh_config.parse(f)
    return ssh_config

def get_all_hostnames(ssh_config=None):
    if ssh_config is None:
        ssh_config = load_ssh_config()
    hostnames = []
    for host in ssh_config._config:
        patterns = host.get('host', [])
        for pattern in patterns:
            if pattern != '*':  # 排除通配符
                hostnames.append(pattern)
    return hostnames

def get_ssh_config(hostname, ssh_config=None):
    if ssh_config is None:
        ssh_config = load_ssh_config()
    host_config = ssh_config.lookup(hostname)
    return host_config

class SSHConnection(object):
    def __init__(self, host_config):
        self.host = host_config['hostname']
        self.port = int(host_config.get('port', 22))
        self.user = host_config.get('user')
        # self.password = password
        self.key_filename = host_config.get('identityfile', [f'{DEFAULT_KEY_PATH}'])[0]
        self.proxy_command = host_config.get('proxycommand', None)

        self.error_callback = None # TODO: error callback from mainwindow, all ssh error shoube be handled by remote object instead of the main viewer object

        self._createSSHClient()

    def _createSSHClient(self):
        # SSH + cat is not encrypted
        client = paramiko.SSHClient()

        # config ProxyCommand
        if self.proxy_command:
            proxy = paramiko.ProxyCommand(self.proxy_command)

        client.load_system_host_keys()
        # add host key automatically in known_hosts
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # if self.password is not None:
        #     client.connect(self.host, self.port, self.user, self.password)
        # else:
        private_key = paramiko.RSAKey(filename=self.key_filename)
        client.connect(
            self.host,
            self.port,
            self.user,
            sock=proxy,
            pkey=private_key
        )
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

    def getAllFiles(self, folder, suffix=('.png', '.jpg', '.jpeg', '.mp4', '.gif'), full_path=False):
        if isinstance(suffix, str):
            suffix = (suffix)
        
        assert isinstance(folder, str), f'folder {folder} should be a string, only single folder supported now.'
        # if isinstance(folder, str):
        #     folder = [folder]

        rule = ' '.join([f'-o -name "*{s}"' for s in suffix])[2:]
        # folder = ' '.join(folder)
        cmd = f'find {folder} -type f \( {rule} \)'
        print(cmd)
        stdin, stdout, stderr = self.client.exec_command(cmd)
        file_list = stdout.read().decode('utf-8').split('\n')
        # remove all empty string
        file_list = sorted([s.strip() for s in file_list if s.strip()])

        if full_path:
            return file_list
        
        # return [os.path.basename(f) for f in file_list]
        print(file_list)
        # relative path
        return [os.path.relpath(f, folder) for f in file_list]

    def __del__(self):
        self.client.close()

def create_ssh_client(hostname, ssh_config=None):
    host_config = get_ssh_config(hostname, ssh_config)
    return SSHConnection(host_config)