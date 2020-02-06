from utils import save_results
import os
import subprocess
import time


def test(num, cmd):
    qemu_cmd = 'timeout 5 qemu-system-i386 -serial mon:stdio -drive file=./submission/xv6.img,media=disk,index=0,format=raw -drive file=./submission/fs.img,media=disk,index=1,format=raw -smp 1 -m 512 -display none -nographic'

    with open('test-{}.in'.format(num), 'w') as f:
        f.write('\n{} README.md\n'.format(cmd))
        f.close()

    qemu = subprocess.Popen(qemu_cmd + ' < test-{}.in'.format(num), stdout=subprocess.PIPE, shell=True)
    expected = subprocess.check_output(cmd + ' ./submission/README.md', shell=True).decode().strip().split('\n')
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

    for index in range(len(expected)):
        expected[index] = expected[index].strip()

    if lines != expected:
        print('your lines:', '\n'.join(lines), sep='\n')
        print('we expected:', '\n'.join(expected), sep='\n')
        save_results('test-{}'.format(num), ['Did not recieve exepected output'], False)
    else:
        print('test passed, we recieved the expected output')
        save_results('test-{}'.format(num), [], True)
