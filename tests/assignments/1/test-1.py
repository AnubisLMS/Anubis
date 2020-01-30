from utils import save_results
import os

os.system('timeout 5 qemu-system-i386 -serial mon:stdio -drive file=./submission/xv6.img,media=disk,index=0,format=raw -drive file=./submission/fs.img,media=disk,index=1,format=raw  -smp 1 -m 512 -display none -nographic')


save_results(
    'test-1',
    ['test error'],
    False
)
