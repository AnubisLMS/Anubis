from utils import save_results
import os
import subprocess
import time
import random
import parse


def test_expected(lines):
    if lines[0].strip() == 'exec wstattest failed':
        return False, 'wstat not properly implemented'

    if len(lines) != 20:
        return False, 'unexpected number of lines'

    for index in range(10):
        if lines[index].strip() != 'child exiting':
            return False, 'unexpected output'

    for index in range(10, 20):
        p = parse.parse(
            'wtime : {}, rtime: {}, iotime: {}, pid {}',
            lines[index].strip()
        )

        if p is None:
            return False, 'invalid output parsed'

    return True, 'valid output parsed'

def test(num, cmd):
    try:
        print()
        print('test-{}:'.format(num))
        print('Testing wstattest program')
        qemu_cmd = 'timeout 5 qemu-system-i386 -serial mon:stdio -drive file=./submission/xv6.img,media=disk,index=0,format=raw -drive file=./submission/fs.img,media=disk,index=1,format=raw -smp 1 -m 512 -display none -nographic'

        print('running: {}'.format(cmd))

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

        passed, err = test_expected(lines)
        if passed:
            print('wstattest works: test passed')
            save_results(
                'test-{}'.format(num),
                [err],
                True
            )
        else:
            print('wstattest does not work: test failed')
            save_results(
                'test-{}'.format(num),
                [err],
                False
            )
    except:
        print('xv6 did not start correctly')
        save_results(
            'test-{}'.format(num),
            ['xv6 did not start correctly'],
            False
        )

test(2, 'wstattest')
