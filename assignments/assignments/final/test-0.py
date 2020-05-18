from utils import save_results
import os
import subprocess
import time


def test_lines(lines, expexted):
    return all(l.startswith(e) for l, e in zip (lines, expexted))

def test(num, cmd):
    try:
        print()
        print('test-0:')
        print('Testing if xv6 starts and prompts for password'.format(cmd))
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

        if not any('init: starting sh' in i for i in lines):
            print('xv6 does start correctly')
            save_results(
                'test-{}'.format(num),
                ['xv6 does start correctly'],
                True
            )
        else:
            print('xv6 did not start correctly')
            save_results(
                'test-{}'.format(num),
                ['xv6 did not start correctly'],
                False
            )
    except:
        print('xv6 did not start correctly')
        save_results(
            'test-{}'.format(num),
            ['xv6 did not start correctly'],
            False
        )

test(0, 'ls')
