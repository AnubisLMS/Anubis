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
        print('If this test passes after you follow the instructions for the coding section, you likely implemented password correctly.')
        qemu_cmd = 'timeout 55 qemu-system-i386 -serial mon:stdio -drive file=./submission/xv6.img,media=disk,index=0,format=raw -drive file=./submission/fs.img,media=disk,index=1,format=raw -smp 1 -m 512 -display none -nographic'

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

        if any('No password set. Please choose one.' in i for i in lines) \
           and any('Password successfully set.' in i for i in lines)\
           and any('init: starting sh' in i for i in lines):
            print('setting password worked')
            save_results(
                'test-{}'.format(num),
                ['setting password worked'],
                True
            )
        else:
            print('setting password did not work')
            save_results(
                'test-{}'.format(num),
                ['setting password did not work'],
                False
            )
    except:
        print('setting password check failed')
        save_results(
            'test-{}'.format(num),
            ['setting password check failed'],
            False
        )

test(1, 'password\npassword\npassword')
