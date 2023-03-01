Please edit the HOST and PORT parameter first.

server: python time_sync.py -s \<filename\>

client: python time_sync.py -c \<filename\>

Use \<filename\> to recongnize time syncronization before/after experiment.

Note: there's little error handling so if output RTT seems weird ( e.g. \< 1ms), please run again.
