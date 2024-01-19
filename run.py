import os
import subprocess
import re


def prepare_tun_device():
    if not os.path.exists('/dev/net/tun'):
        if not os.path.exists('/dev/net'):
            os.mkdir('/dev/net')
        os.mknod('/dev/net/tun', 0o755, os.makedev(10, 200))
    
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
    start_params = None

    try:
        subprocess.check_output(['protonvpn', 'refresh'])

        args = ['protonvpn', 'connect']

        if os.environ.get('PVPN_ARGS'):
            start_params = [a for a in re.split(r' +', os.environ.get('PVPN_ARGS')) if a]
        else:
            start_params = ['--fastest']

        args += start_params
        
        subprocess.check_output(args)
        subprocess.check_output(['ip', 'link', 'show', 'proton0'])
    except (Exception,):
        raise RuntimeError('Failed to run ProtonVPN')
    
    print(f'ProtonVPN started! (using params: {" ".join(start_params)})')


def run_pproxy():
    args = ['pproxy']
    start_params = None

    if os.environ.get('PPROXY_ARGS'):
        start_params = [a for a in re.split(r' +', os.environ.get('PPROXY_ARGS')) if a]
        args += start_params
    
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    
    if start_params:
        print(f'PProxy started! (using params: {" ".join(start_params)})')
    else:
        print('PProxy started!')

    while proc.poll() is None:
        line = proc.stdout.readline()
        if line:
            print(line.decode('utf-8').strip())
    
    if proc.returncode != 0:
        raise RuntimeError('Failed to run PProxy')
    

def main():
    prepare_tun_device()
    prepare_protonvpn_config()
    run_protonvpn()
    run_pproxy()


if __name__ == '__main__':
    main()
