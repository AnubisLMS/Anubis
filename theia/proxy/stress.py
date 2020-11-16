import multiprocessing as mp
import requests
import time
import urllib3

urllib3.disable_warnings()
def func(_):
    requests.get('https://proxy.localhost/bundle.js', verify=False)

n=10000
start = time.time()
with mp.Pool(10) as pool:
    pool.map(func, [None]*n)
    pool.close()
elapsed = time.time() - start
print('took {:0.2f}s for {} requests'.format(elapsed, n))
print('{:0.2f} req/s'.format(float(n)/elapsed))
