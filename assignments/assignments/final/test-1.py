from utils import save_results
import os
import subprocess
import time
import json
from parse import compile


def test(num, cmd):
    try:
        print()
        print('test-1:')
        print('Testing if correct password works')
        print('If you this test passes after you follow the instructions for the coding section, you likely implemented password correctly.')
        qemu_cmd = 'timeout 15 qemu-system-i386 -serial mon:stdio -drive file=./submission/xv6.img,media=disk,index=0,format=raw -drive file=./submission/fs.img,media=disk,index=1,format=raw -smp 1 -m 512 -display none -nographic'

        with open('test-{}.in'.format(num), 'w') as f:
            f.write('\n{}\n'.format(cmd))
            f.close()

        qemu = subprocess.Popen(qemu_cmd + ' < test-{}.in'.format(num), stdout=subprocess.PIPE, shell=True)
        qemu.wait()
        stdout, err = qemu.communicate()
        stdout = stdout.decode().split('\n')
        lines = stdout[:]

        if any('unexpected trap' in i or 'cpu0: panic' in i for i in lines):
            raise Exception()

        print(json.dumps(lines, indent=2))

        while len(lines) != 0 and (lines[-1].startswith('$') or len(lines[-1].strip()) == 0):
            lines.pop()

        if len(lines) != 0 and lines[0].startswith('$'):
            lines[0] = lines[0].lstrip('$').strip()

        for index in range(len(lines)):
            lines[index] = lines[index].strip()

        print(lines)

        if any('No password set. Please choose one.' in i for i in lines) \
           and any('Password successfully set. You may now use it to log in.' in i for i in lines)\
           and any('Password correct, logging you in.' in i for i in lines):
            print('init: starting sh')
            save_results(
                'test-{}'.format(num),
                ['correct password worked'],
                True
            )
        else:
            print('correct password did not work')
            save_results(
                'test-{}'.format(num),
                ['correct password did not work'],
                False
            )
    except:
        print('password check failed')
        save_results(
            'test-{}'.format(num),
            ['password check failed'],
            False
        )

test(1, 'password\npassword\npassword')
