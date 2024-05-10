import os
import sys

"""
Offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, LteRrcAnalyzer, WcdmaRrcAnalyzer, LteNasAnalyzer, UmtsNasAnalyzer, LtePhyAnalyzer, LteMacAnalyzer, NrRrcAnalyzer, LteMeasurementAnalyzer 
from mobile_insight.analyzer import MyAnalyzer

def analysis(path):
    
    print("Analyzing -- ", path)

    src = OfflineReplayer()
    src.set_input_path(path)

    logger = MsgLogger()
    logger.set_decode_format(MsgLogger.XML)
    logger.set_dump_type(MsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as(path+".txt")
    logger.set_source(src)
    
    # Analyzers
    # lte_rrc_analyzer = LteRrcAnalyzer()
    # lte_rrc_analyzer.set_source(src)  # bind with the monitor

    # Start the monitoring
    src.run()


if __name__ == "__main__":

    if os.path.isdir(sys.argv[1]):

        dirpath = sys.argv[1]
        filenames = os.listdir(dirpath)

        for each_file in filenames:
            if not each_file.endswith(".mi2log"):
                continue
            path = os.path.join(sys.argv[1], each_file)
            analysis(path)

    elif sys.argv[1].endswith(".mi2log"):
         
         path = sys.argv[1]
         analysis(path)

    else:
        print('WTF did you just give me!!')