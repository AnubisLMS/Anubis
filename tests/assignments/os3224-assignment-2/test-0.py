from utils import save_results
import os
import subprocess
import time

man="""
We will be runnning your guess 10 times. If any, but not all are correct, then
you the expected output will be met.
"""

print(man)


def test_lines(lines, expexted):
    return all(l.startswith(e) for l, e in zip (lines, expexted))

def test(num):
    qemu_cmd = 'timeout 3 qemu-system-i386 -drive file=./submission/guess,media=disk,index=0,format=raw -nographic  -display none '
    try:
        qemu = subprocess.Popen(qemu_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=None, shell=True)
        for line in iter(qemu.stdout.readline, ''):
            if line.decode().startswith('Booting from Hard Disk'):
                time.sleep(0.5)
                stdout, _ = qemu.communicate(str(num).encode(), 3)
                break
            # if len(line) > 0:
            #     print(line)
        #qemu.wait()
        #stdout, err = qemu.communicate()
        stdout = stdout.decode().split('\n')
        return stdout[-1].startswith('Right')
    except Exception as e:
        print('Exception:', e)
        save_results(
            'test-0',
            ['an unexpected error occured, admins will be notified'],
            False
        )
        exit(1)


if __name__ == "__main__":
    res = [
        test(i)
        for i in range(10)
    ]
    if any(res) and not all(res):
        print('test-0 passed')
        save_results(
            'test-0',
            ['guess.s seems to be functioning properly'],
            True
        )
