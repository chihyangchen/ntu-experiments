## time_sync.py

Please edit the HOST and PORT parameter first.

### usage
```
python time_sync.py <-s or -c> <-b or -a>
```

-s, -c, -b, -a stand for server, client, before, after, respectively.

Note: there's little error handling so if output RTT seems weird (e.g. \< 0 ms), please run again.

## clock_diff.py

### usage

#### clock_diff()

Return 4 variables: ``ref_time1``, ``ref_time2``, ``diff1``, ``diff2``,
the reference timestamp and clock difference at that time before or after the experiment.
``diff1`` and ``diff2`` is the time server faster than client (unit: second.)

#### server_time_to_client_time(server_time, ref_time1, ref_time2, diff1, diff2)

Convert a server timestamp to client timestamp.
