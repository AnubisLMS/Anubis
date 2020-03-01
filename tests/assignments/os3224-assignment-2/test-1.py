from utils import save_results
import os
import subprocess
import time
import random



l1 = list(sorted(random.randint(0, 20) for _ in range(random.randint(5, 10))))
l2 = list(sorted(random.randint(0, 20) for _ in range(random.randint(5, 10))))

ans = list(sorted(l1 + l2))

expected = '->'.join(str(i) for i in ans)

print('list1:', ' '.join(str(i) for i in l1))
print('list2:', ' '.join(str(i) for i in l2))
print('expected output:', expected)
print(
    'command being run: ./linkedList',
    ' '.join(str(i) for i in l1),
    ',',
    ' '.join(str(i) for i in l2),
)


def test():
    try:
        prog = subprocess.Popen(
            ['./submission/linkedList'] + [str(i) for i in l1] + [','] + [str(i) for i in l2],
            stdout=subprocess.PIPE,
            stderr=None
        )
        prog.wait()
        stdout, err = prog.communicate()
        stdout = stdout.decode().split('\n')
        print('output lines parsed:', stdout)
        ans = [line.startswith(expected) for line in stdout]
        if any(ans):
            print('expected result was found')
            return save_results(
                'test-1',
                ['expected result was found'],
                True
            )
    except:
        pass

    save_results(
        'test-1',
        ['expected result was not found'],
        False
    )

test()
