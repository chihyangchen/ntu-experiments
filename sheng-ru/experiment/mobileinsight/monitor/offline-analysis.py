import os
import sys

"""
Offline analysis by replaying logs
"""

# Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from mobile_insight.analyzer import MsgLogger, MyMsgLogger, LteRrcAnalyzer, WcdmaRrcAnalyzer, LteNasAnalyzer, UmtsNasAnalyzer, LtePhyAnalyzer, LteMacAnalyzer, NrRrcAnalyzer, LteMeasurementAnalyzer 
from mobile_insight.analyzer import FeatureExtracter

def analysis(path):
    
    print("Analyzing -- ", path)

    src = OfflineReplayer()
    src.set_input_path(path)

    logger = MyMsgLogger()
    logger.set_decode_format(MyMsgLogger.XML)
    logger.set_dump_type(MyMsgLogger.FILE_ONLY)
    logger.save_decoded_msg_as(path+".txt")
    logger.set_source(src)
    
    src.enable_log("5G_NR_RRC_OTA_Packet")
    src.enable_log("LTE_RRC_OTA_Packet")
    # src.enable_log("LTE_PHY_Serv_Cell_Measurement")
    # src.enable_log("5G_NR_ML1_Searcher_Measurement_Database_Update_Ext")
    # src.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Meas")
    # src.enable_log("LTE_NB1_ML1_GM_DCI_Info")

    # Analyzers
    # lte_rrc_analyzer = LteRrcAnalyzer()
    # lte_rrc_analyzer.set_source(src)  # bind with the monitor
    
    # nr_rrc_analyzer = NrRrcAnalyzer()
    # nr_rrc_analyzer.set_source(src)
    
    # wcdma_rrc_analyzer = WcdmaRrcAnalyzer()
    # wcdma_rrc_analyzer.set_source(src)  # bind with the monitor
    
    # lte_nas_analyzer = LteNasAnalyzer()
    # lte_nas_analyzer.set_source(src)
    
    # umts_nas_analyzer = UmtsNasAnalyzer()
    # umts_nas_analyzer.set_source(src)
    
    # lte_phy_analyzer = LtePhyAnalyzer()
    # lte_phy_analyzer.set_source(src)
    
    # lte_mac_analyzer = LteMacAnalyzer()
    # lte_mac_analyzer.set_source(src)
    
    # lte_meas_analyzer = LteMeasurementAnalyzer()  
    # lte_meas_analyzer.set_source(src)

    # My Analyzer
    # my_analyzer = MyAnalyzer()
    # my_analyzer.set_source(src)

    # feature_extracter = FeatureExtracter(mode='intensive')
    # feature_extracter.set_source(src)

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