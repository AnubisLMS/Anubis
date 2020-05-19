from utils import save_results
import os
import subprocess
import time
import json
from parse import compile


def test(num, cmd):
    try:
        print()
        print('test-3:')
        print('Testing if correct password is rejected')
        print('If this test passes after you follow the instructions for the coding section, you likely implemented password correctly.')
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

        if any('Enter password:' in i for i in lines) and \
           any('init: starting sh' in i for i in lines):
            print('correct password was accepted')
            save_results(
                'test-{}'.format(num),
                ['correct password was accepted'],
                True
            )
        else:
            print('correct password was not accepted')
            save_results(
                'test-{}'.format(num),
                ['correct password was not accepted'],
                False
            )
    except:
        print('password check failed')
        save_results(
            'test-{}'.format(num),
            ['password check failed'],
            False
        )

test(3, 'password')
