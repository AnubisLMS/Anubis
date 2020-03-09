from utils import save_results
import os
import subprocess
import time
import json
from parse import compile

def test_fork(lines):
    if len(lines) == 0:
        return False, 'no lines parsed'

    print('$ schedtest')
    print(*lines, sep='\n')

    if lines[0].startswith('sched test'):
        lines.pop(0)

    for line in lines:
        if 'panic' in lines:
            return False, 'panic parsed'

    if len(lines) != 20:
        return False, 'line count is not correct'

    s = compile('start {:d}')
    e = compile('end {:d}')

    for i in range(0, len(lines), 2):
        start = s.parse(lines[i])
        end = e.parse(lines[i+1])

        if start is None or end is None:
            return False, 'unexpected line order, or parse error'

        start = start.fixed[0]
        end = end.fixed[0]

        if start != end:
            return False, 'schedule order unexpected'

    return True, 'expected output was found'



def test(num, cmd):
    try:
        print()
        print('test-1:')
        print('Testing first come first serve using schedtest')
        qemu_cmd = 'timeout 28 qemu-system-i386 -serial mon:stdio -drive file=./submission/xv6.img,media=disk,index=0,format=raw -drive file=./submission/fs.img,media=disk,index=1,format=raw -smp 1 -m 512 -display none -nographic'

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

        passed, err = test_fork(lines)

        if passed:
            print('test passed:', err)
        else:
            print('test failed:', err)

        save_results(
            'test-{}'.format(num),
            [err],
            passed
        )
    except:
        print('error while testing first come first serve scheduling')
        save_results(
            'test-{}'.format(num),
            ['error while testing first come first serve scheduling'],
            False
        )

test(1, 'schedtest')

# lines = [
#     "start 13",
# "end 13",
# "start 12",
# "end 12",
# "start 11",
# "end 11",
# "start 10",
# "end 10",
# "start 9",
# "end 9",
# "start 8",
# "end 8",
# "start 7",
# "end 7",
# "start 6",
# "end 6",
# "start 5",
# "end 5",
# "start 4",
# "end 4",
# ]

# passed, err = test_fork(lines)
# print (passed, err)
