from utils import save_results
import os
import subprocess
import time
import random


def test_lines(lines, expected):
    return any(l.strip() == expected.strip() for l in lines)

def test(num):
    try:
        print()
        print('test-6:')
        print('Testing testmynetid')
        qemu_cmd = 'timeout 5 qemu-system-i386 -serial mon:stdio -drive file=./submission/xv6.img,media=disk,index=0,format=raw -drive file=./submission/fs.img,media=disk,index=1,format=raw -smp 1 -m 512 -display none -nographic'

        cmd = 'testmynetid'
        expected = os.environ['NETID']

        print('running: {}'.format(cmd))
        print('expecting output: {}'.format(expected))

        with open('test-{}.in'.format(num), 'w') as f:
            f.write('\n{}\n'.format(cmd))
            f.close()

        qemu = subprocess.Popen(qemu_cmd + ' < test-{}.in'.format(num), stdout=subprocess.PIPE, shell=True)
        qemu.wait()
        stdout, err = qemu.communicate()
        stdout = stdout.decode().split('\n')
        lines = stdout[stdout.index('init: starting sh')+1:]

        if lines[0].startswith('$'):
            lines[0] = lines[0].lstrip('$').strip()

        if lines[-1].strip() == '$':
            lines.pop()

        for index in range(len(lines)):
            lines[index] = lines[index].strip()

        print('lines parsed:', lines)

        if test_lines(lines, expected):
            print('testmynetid works: test passed')
            save_results(
                'test-{}'.format(num),
                ['testmynetid works'],
                True
            )
        else:
            print('testmynetid does not work: test failed')
            save_results(
                'test-{}'.format(num),
                ['testmynetid does not work'],
                False
            )
    except:
        print('xv6 did not start correctly')
        save_results(
            'test-{}'.format(num),
            ['xv6 did not start correctly'],
            False
        )

test(6)
