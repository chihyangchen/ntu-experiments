## time_sync.py

Please edit the HOST and PORT parameter first.

## usage
```
server: python time_sync.py -s <--start or --end>
client: python time_sync.py -c <--start or --end>
```

Use \<--start or --end\> to recongnize time syncronization before/after experiment.

Note: there's little error handling so if output RTT seems weird (e.g. \< 1ms), please run again.
