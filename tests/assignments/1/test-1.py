from utils import save_results
import os

os.system('timeout -s 5 qemu-system-i386 -serial mon:stdio -drive file=xv6.img,media=disk,index=0,format=raw -drive file=fs.img,index=1,media=disk,format=raw -smp $(CPUS) -m 512 $(QEMUEXTRA) -display none -nographic')


save_results(
    'test-1',
    ['test error'],
    False
)
