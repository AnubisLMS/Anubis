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
        print('Testing if xv6 starts'.format(cmd))
        qemu_cmd = 'timeout 5 qemu-system-i386 -serial mon:stdio -drive file=./submission/xv6.img,media=disk,index=0,format=raw -drive file=./submission/fs.img,media=disk,index=1,format=raw -smp 1 -m 512 -display none -nographic'

        with open('test-{}.in'.format(num), 'w') as f:
            f.write('\n{}\n'.format(cmd))
            f.close()

        qemu = subprocess.Popen(qemu_cmd + ' < test-{}.in'.format(num), stdout=subprocess.PIPE, shell=True)
        qemu.wait()
        stdout, err = qemu.communicate()
        stdout = stdout.decode().split('\n')
        lines = stdout[stdout.index('init: starting sh')+1:]


        while lines[-1].startswith('$') or len(lines[-1].strip()) == 0:
            lines.pop()

        if lines[0].startswith('$'):
            lines[0] = lines[0].lstrip('$').strip()

        for index in range(len(lines)):
            lines[index] = lines[index].strip()

        if len(lines) > 0:
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
