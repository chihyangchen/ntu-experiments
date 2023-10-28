import subprocess
import os
import sys
import time

def pcap_to_csv(infilepath, outfilepath):
    # TCP
    # s = f"tshark -r {infilepath} -T fields -e frame.number -e frame.time -e ip.src -e ip.dst -e _ws.col.Protocol "\
    #     "-e frame.len -e tcp.analysis.acks_frame -e tcp.seq_raw -e tcp.len -e tcp.analysis.ack_rtt -e tcp.srcport "\
    #     "-e tcp.dstport -e tcp.analysis.bytes_in_flight -e tcp.analysis.retransmission -e tcp.analysis.fast_retransmission "\
    #     f"-e tcp.analysis.out_of_order -E header=y -E separator=@ >{outfilepath}"
    
    # UDP
    s = f"tshark -r {infilepath} -T fields -e frame.number -e frame.time -e frame.len \
        -e sll.pkttype -e _ws.col.Protocol -e ip.proto -e ip.len -e ip.src -e ip.dst \
        -e udp.length -e udp.srcport -e udp.dstport -e data.len -e udp.payload -e _ws.col.Info \
        -E header=y -E separator=@ > {outfilepath}"
    
    print(s)
    subprocess.Popen([s], shell=True)
    time.sleep(5)

if os.path.isdir(sys.argv[1]):

    dirname = sys.argv[1]

    filenames = os.listdir(dirname)

    for fname in sorted(filenames):
        if not fname.endswith(".pcap"):
            continue

        pcap_to_csv(os.path.join(dirname, fname), os.path.join(dirname, fname[:fname.find(".pcap")]+"_pcap.csv"))

elif sys.argv[1].endswith(".pcap"):

    fname = sys.argv[1]
    pcap_to_csv(fname, os.path.join(fname[:fname.find(".pcap")]+"_pcap.csv"))

else:
    print("what the hell is", sys.argv[1])