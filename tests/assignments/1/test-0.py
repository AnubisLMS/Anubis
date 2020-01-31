from utils import save_results
import os
import subprocess
import time

qemu_cmd = 'timeout 5 qemu-system-i386 -serial mon:stdio -drive file=./submission/xv6.img,media=disk,index=0,format=raw -drive file=./submission/fs.img,media=disk,index=1,format=raw -smp 1 -m 512 -display none -nographic'

def test_1():
    qemu = subprocess.Popen(qemu_cmd + ' <<< "\nuniq README.md\n"', stdout=subprocess.PIPE, shell=True)
    expected = subprocess.check_output('uniq ./submission/README.md', shell=True)
    qemu.wait()
    stdout, err = qemu.communicate()
    stdout = stdout.decode().split('\n')
    lines = stdout[stdout.index('init: starting sh'):]
    

try:
    pass
except:
    save_results(
        'test-0',
        ['nah'],
        False
    )
