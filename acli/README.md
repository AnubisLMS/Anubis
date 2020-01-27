# ACLI

## List active jobs
```bash
acli ls
```


## Restart / re-enqueue job
```bash
acli 'abc123'                       # restarts most recently processed job for that netid
acli 'abc123' 'assignment' 'commit' # re-enqueues job based on those params
```

