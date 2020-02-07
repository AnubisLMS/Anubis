from utils import save_results
import os
import subprocess
import time

print('Running: hello')
print('We expect the output: Hello world')

qemu_cmd = 'timeout 5 qemu-system-i386 -serial mon:stdio -drive file=./submission/xv6.img,media=disk,index=0,format=raw -drive file=./submission/fs.img,media=disk,index=1,format=raw -smp 1 -m 512 -display none -nographic'


try:
    with open('test-0.in', 'w') as f:
        f.write('\nhello\n')
        f.close()

    qemu = subprocess.Popen(qemu_cmd + ' < test-0.in', stdout=subprocess.PIPE, shell=True)
    qemu.wait()
    stdout, err = qemu.communicate()
    stdout = stdout.decode().split('\n')
    lines = stdout[stdout.index('init: starting sh')+1:]

    try:
        while lines[-1].startswith('$') or len(lines[-1].strip()) == 0:
            lines.pop()
    except:
        save_results(
            'test-0',
            ['We could not parse any output. Did the program get compiled?'],
            False
        )
    if lines[0].startswith('$'):
        lines[0] = lines[0].lstrip('$').strip()

    for index in range(len(lines)):
        lines[index] = lines[index].strip()

    if any(l.lower() == 'Hello world' for l in lines):
        print('your lines:', '\n'.join(lines), sep='\n')
        print('we expected:', '\n'.join(['Hello world']), sep='\n')
        save_results(
            'test-0',
            ['Did not recieve exepected output'],
            False
        )
    else:
        print('test passed, we recieved the expected output')
        save_results(
            'test-0',
            [],
            True
        )
except:
    save_results(
        'test-0',
        ['an unexpected error occured, admins will be notified'],
        False
    )
    exit(1)
