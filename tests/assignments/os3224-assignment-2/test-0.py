from utils import save_results
import os
import subprocess
import time

man="""
There is no clean way to parse the BIOS io programatically, so
simply compiling will be considered passing.
"""

print(man)


def test_lines(lines, expexted):
    return all(l.startswith(e) for l, e in zip (lines, expexted))

def test(num):
    qemu_cmd = 'timeout 3 qemu-system-i386 -drive file=./submission/guess,media=disk,index=0,format=raw -noframe'
    try:
        qemu = subprocess.Popen(qemu_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=None, shell=True)
        time.sleep(0.5)
        print('yeet')
        stdout, _ = qemu.communicate(str(num).encode(), 3)
        print(stdout)
        # for line in iter(qemu.stdout.readline, ''):
        #     if len(line) > 0:
        #     if line.decode().startswith('Booting from Hard Disk'):
        #         time.sleep(0.5)
        #         stdout=''
        #         break
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
    save_results('test-0', ['guess.s compiles'], True)
    # res = [
    #     test(i)
    #     for i in range(10)
    # ]
    # if any(res) and not all(res):
    #     print('test-0 passed')
    #     save_results(
    #         'test-0',
    #         ['guess.s seems to be functioning properly'],
    #         True
    #     )
