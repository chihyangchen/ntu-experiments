from .analyzer import *

class TimeSyncAnalyzer(Analyzer):
    
    def __init__(self, save_path=None):
        
        Analyzer.__init__(self)
        
        if self.save_path:
            self.f = open(self.save_path, 'w')
        
         # init packet filters
        self.add_source_callback(self.ue_event_filter)
        
    def set_source(self, source):
        """
        Set the source of the trace.
        Enable device's LTE internal logs.
        :param source: the source trace collector
        :param type: trace collector
        """
        Analyzer.set_source(self, source)
        # enable user's internal events
        source.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Meas")
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("5G_NR_RRC_OTA_Packet")
        source.enable_log("5G_NR_ML1_Searcher_Measurement_Database_Update_Ext")

    def ue_event_filter(self, msg):
        # TODO: support more user events
        self.test(msg)
    
    # For testing
    def test(self, msg):
        if msg.type_id == "LTE_PHY_Connected_Mode_Intra_Freq_Meas":
            
            msg_dict = dict(msg.data.decode())
            date = msg_dict['timestamp']
            d = date.replace(microsecond=0)
            print(d)