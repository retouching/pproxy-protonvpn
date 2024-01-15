import os
import subprocess


def prepare_tun_device():
    if not os.path.exists('/dev/net/tun'):
        if not os.path.exists('/dev/net'):
            os.mkdir('/dev/net')
        subprocess.check_output(['mknod', '/dev/net/tun', 'c', '10', '200'])
    
    print('Tun device initialized!')


def prepare_protonvpn_config():
    PVPN_PATH = '/root/.pvpn-cli'

    if not os.environ.get('PVPN_USERNAME') or not os.environ.get('PVPN_PASSWORD') or not os.environ.get('PVPN_TIER'):
        raise Exception('PVPN_USERNAME, PVPN_PASSWORD and PVPN_TIER environment variables must be set')
    
    for file in ['pvpnpass', 'pvpn-cli.cfg']:
        if os.path.exists(os.path.join(PVPN_PATH, file)):
            os.unlink(os.path.join(PVPN_PATH, file))

    with open(os.path.join(PVPN_PATH, 'pvpn-cli.cfg.clean'), 'r') as fc:
        with open(os.path.join(PVPN_PATH, 'pvpn-cli.cfg'), 'w') as f:
            data = fc.read()

            data = data.replace('PVPN_USERNAME', os.environ.get('PVPN_USERNAME'))
            data = data.replace('PVPN_TIER', os.environ.get('PVPN_TIER'))
            data = data.replace('PVPN_PROTOCOL', 'udp')
    
            f.write(data)

    with open(os.path.join(PVPN_PATH, 'pvpnpass'), 'w') as f:
        f.write(f'{os.environ.get("PVPN_USERNAME")}\n{os.environ.get("PVPN_PASSWORD")}')
    
    os.chmod(os.path.join(PVPN_PATH, 'pvpnpass'), 0o600)

    print('ProtonVPN config initialized!')


def run_protonvpn():
    try:
        subprocess.check_output(['protonvpn', 'refresh'])

        args = ['protonvpn', 'connect']

        if os.environ.get('PVPN_COUNTRY'):
            args += ['--cc', os.environ.get('PVPN_COUNTRY')]
        elif os.environ.get('PVPN_SERVER'):
            args += [os.environ.get('PVPN_SERVER')]
        else:
            args += ['--fastest']
        
        subprocess.check_output(args)
        subprocess.check_output(['ip', 'link', 'show', 'proton0'])
    except (Exception,):
        raise RuntimeError('Failed to run ProtonVPN')
    
    print('ProtonVPN started!')


def run_pproxy():
    if not os.environ.get('PPROXY_LISTEN'):
        raise Exception('PPROXY_LISTEN environment variable must be set')
    
    try:
        subprocess.check_output(['pproxy', '-l', os.environ.get('PPROXY_LISTEN')])
    except (Exception,):
        raise RuntimeError('Failed to run pproxy')
    

def main():
    prepare_tun_device()
    prepare_protonvpn_config()
    run_protonvpn()
    run_pproxy()


if __name__ == '__main__':
    main()
