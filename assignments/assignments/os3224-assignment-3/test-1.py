from utils import save_results
import os
import subprocess
import time
from parse import compile

def test_fork(lines):
    if len(lines) == 0:
        return False, 'no lines parsed'

    if lines[0].startswith('fork test'):
        lines.pop(0)

    if len(lines) != 120:
        return False, 'line count is not correct'

    print(*lines, sep='\n')

    p = compile('im {:d} and my child had pid {:d}')
    c = compile('my pid is {:d}')

    last_ppid = None

    for i in range(0, len(lines), 2):
        pline = lines[i]
        cline = lines[i+1]

        ppid, cpid = p.parse(pline)
        ccpid = c.parse(cline).fixed[0]

        if cpid != ccpid:
            return False, 'mismatched output lines'

        if last_ppid is not None:
            if last_ppid != ppid:
                return False, 'mismatched output lines'
        last_ppid = cpid
    return True, 'expected output was found'



def test(num, cmd):
    try:
        print()
        print('Testing first come first serve using forktest')
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


        save_results(
            'test-{}'.format(num),
            [err],
            passed
        )
    except:
        pass
        # print('xv6 did not start correctly')
        # save_results(
        #     'test-{}'.format(num),
        #     ['xv6 did not start correctly'],
        #     False
        # )
    passed, err = test_fork(lines)
    print(passed, err)

test(0, 'forktest')
