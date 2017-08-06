import stat
import sys
import os

def main():
    print('Welcome to the TWOWBot setup utility!')
    print('=====================================')

    sys.stdout.write('Checking python version  [       ]')
    sys.stdout.flush()
    python_version = sys.version_info
    
    print('\rChecking python version  [ {}.{}.{} ]'.format(*python_version))
    if python_version[0] != 3 or python_version[1] != 6:
        print('You must be using Python 3.6 for TWOWBot to work.')
        return
    
    sys.stdout.write('Checking for discord.py  [       ]')
    sys.stdout.flush()
    try:
        import discord
    except ImportError:
        print('\rChecking for discord.py  [FAILED!]')
        print('Installing discord.py:')
        import pip
        result = pip.main(['install', '-U', 'git+https://github.com/Rapptz/discord.py@rewrite'])
        if result != 0:
            print('Something went wrong while installing discord.py!')
            return
    else:
        print('\rChecking for discord.py  [ FOUND ]')
    
    sys.stdout.write('Checking for ruamel.YAML [       ]')
    sys.stdout.flush()
    try:
        import ruamel.yaml
    except ImportError:
        print('\rChecking for ruamel.YAML [FAILED!]')
        print('Installing ruamel.YAML:')
        import pip
        result = pip.main(['install', '-U', 'ruamel.YAML'])
        if result != 0:
            print('Something went wrong while installing ruamel.YAML')
            return
    else:
        print('\rChecking for ruamel.YAML [ FOUND ]')
    
    sys.stdout.write('Creating data files      [       ]')
    sys.stdout.flush()
    os.chdir('src')
    if 'config.yml' not in os.listdir('.'):
        with open('config.yml.template') as template:
            with open('config.yml', 'w') as target:
                target.write(template.read())
                config = True
    else:
        config = False
    os.chdir('server_data')
    if 'servers.yml' not in os.listdir('.'):
        with open('servers.yml.template') as template:
            with open('servers.yml', 'w') as target:
                target.write(template.read())
    print('\rCreating data files      [ DONE  ]')
    
    sys.stdout.write('Setting up start scripts [       ]')
    sys.stdout.flush()
    
    os.chdir('../scripts')
    st = os.stat('run_bot.sh')
    os.chmod('run_bot.sh', st.st_mode | (st.st_mode & 0o444) >> 2)
    st = os.stat('run_bot.bat')
    os.chmod('run_bot.bat', st.st_mode | (st.st_mode & 0o444) >> 2)
    print('\rSetting up start scripts [ DONE  ]')
    
    os.chdir('../..')
    print('=====================================')
    if not config:
        print('TWOWBot has been succesfully setup!')
    else:
        print('TWOWBot has mostly been setup.')
        print('You still need to configure config.yml')
        print('Please see the https://github.com/HTSTEM/TWOW_Bot for instructions on this.')


if __name__ == '__main__':
    main()