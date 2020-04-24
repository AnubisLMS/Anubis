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
        print('Testing if cat works')
        print('If you this test passes after you follow the instructions for part B through D, you likely did lazy allocation correctly.')
        qemu_cmd = 'timeout 5 qemu-system-i386 -serial mon:stdio -drive file=./submission/xv6.img,media=disk,index=0,format=raw -drive file=./submission/fs.img,media=disk,index=1,format=raw -smp 1 -m 512 -display none -nographic'

        with open('test-{}.in'.format(num), 'w') as f:
            f.write('\n{}\n'.format(cmd))
            f.close()

        qemu = subprocess.Popen(qemu_cmd + ' < test-{}.in'.format(num), stdout=subprocess.PIPE, shell=True)
        qemu.wait()
        stdout, err = qemu.communicate()
        stdout = stdout.decode().split('\n')
        lines = stdout[stdout.index('init: starting sh')+1:]

        if any('unexpected trap' in i or 'cpu0: panic' in i for i in lines):
            raise Exception()

        while lines[-1].startswith('$') or len(lines[-1].strip()) == 0:
            lines.pop()

        if lines[0].startswith('$'):
            lines[0] = lines[0].lstrip('$').strip()

        for index in range(len(lines)):
            lines[index] = lines[index].strip()

        if len(lines) == 72 \
           and lines[0] == '# VSCode Integration' \
           and lines[-1] == 'requires the "mpage" utility.  See http://www.mesa.nl/pub/mpage/.':
            print('cat program worked correctly')
            save_results(
                'test-{}'.format(num),
                ['cat program worked correctly'],
                True
            )
        else:
            print('cat program did not work correctly')
            save_results(
                'test-{}'.format(num),
                ['cat program did not work correctly'],
                False
            )
    except:
        print('cat program did not work correctly')
        save_results(
            'test-{}'.format(num),
            ['cat program did not work correctly'],
            False
        )

test(1, 'cat README.md | cat')
