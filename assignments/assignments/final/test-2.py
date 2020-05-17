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
        qemu_cmd = 'timeout 5 qemu-system-i386 -serial mon:stdio -drive file=./submission/xv6.img,media=disk,index=0,format=raw -drive file=./submission/fs.img,media=disk,index=1,format=raw -smp 1 -m 512 -display none -nographic'

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

        while len(lines) != 0 and (lines[-1].startswith('$') or len(lines[-1].strip()) == 0):
            lines.pop()

        if len(lines) != 0 and lines[0].startswith('$'):
            lines[0] = lines[0].lstrip('$').strip()

        for index in range(len(lines)):
            lines[index] = lines[index].strip()


        if not any('init: starting sh' i for i in lines):
            print('incorrect password was rejected')
            save_results(
                'test-{}'.format(num),
                ['incorrect password was rejected'],
                True
            )
        else:
            print('incorrect password was not rejected')
            save_results(
                'test-{}'.format(num),
                ['correct password was not rejected'],
                False
            )
    except:
        print('password check failed')
        save_results(
            'test-{}'.format(num),
            ['password check failed'],
            False
        )

test(2, '\nnotpassword')
