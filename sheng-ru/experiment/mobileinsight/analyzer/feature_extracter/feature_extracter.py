    #!/usr/bin/python
# Filename: lte_measurement_analyzer.py

"""
Devise your own analyzer
"""

from .analyzer import *

from .utils.lte_ss_collector import LteSignalStrengthCollector, ss_dict
from .utils.nr_ss_collector import NrSignalStrengthCollector, nr_ss_dict
from .utils.rrc_information import Rrc_Information_Collector

from collections import namedtuple
import copy
import time 
import datetime as dt

class FeatureExtracter(Analyzer):
    """
    An self-defined analyzer
    """
    def __init__(self, save_path='', mode='default'):

        Analyzer.__init__(self)

        # save log
        self.save_path = save_path
        if self.save_path:
            self.f = open(save_path, 'w')

        # init packet filters
        self.add_source_callback(self.ue_event_filter)

        # init class for helping get feature
        self.lte_ss_collector = LteSignalStrengthCollector()
        self.nr_ss_collector = NrSignalStrengthCollector()
        self.rrc_info_collector = Rrc_Information_Collector()
        
        self.featuredict = {
            'LTE_HO': 0, 'MN_HO': 0, 'SN_setup': 0, 'SN_Rel': 0, 'SN_HO': 0, 'RLF': 0, 'SCG_RLF': 0,
            "eventA1": 0, "eventA2": 0, "E-UTRAN-eventA3": 0, "eventA5": 0, "NR-eventA3": 0, "eventB1-NR-r15": 0,
            'num_of_neis': 0,'RSRP': 0, 'RSRQ': 0, 'RSRP1': 0, 'RSRQ1': 0, 'RSRP2': 0, 'RSRQ2': 0, 
            'nr-RSRP': 0, 'nr-RSRQ': 0, 'nr-RSRP1': 0, 'nr-RSRQ1': 0, 'nr-RSRP2': 0, 'nr-RSRQ2':0
        }
        self.features_buffer = copy.deepcopy(self.featuredict)
        
        self.mode = mode
        if self.mode == 'intensive':
            self.lte_ss_L =[] # (time, dict)
            self.nr_ss_L = [] # (time, dict)
            self.rrc_L = [] # (time, dict)
        self.offline_test_dict = {k: [] for k in self.featuredict.keys()}
        
        self.cell_info = {'MN': None, 'earfcn': None, 'band': None,'SN': None}
        self.earfcn_band_pair = {'525':'1', 
                                 '1400': '3', '1750': '3', 
                                 '3050': '7', '3400': '7', 
                                 '3650': '8'}

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
        """
        callback to handle user events
        :param source: the source trace collector
        :param type: trace collector
        """
        # TODO: support more user events
        self.signal_strength(msg)
        self.nr_signal_strength(msg)
        self.ho_events(msg)
        if self.save_path:
            self.record_msg(msg)
            
        # self.offline_test(msg)

    # Unified function
    def record_msg(self, msg):
        print(msg.data.decode(), file = self.f)

    def to_featuredict(self):
        self.ss_dict_to_featuredict()
        self.nr_ss_dict_to_featuredict()
        self.rrc_dict_to_featuredict()

    def reset(self):
        self.lte_ss_collector.reset()
        self.nr_ss_collector.reset()
        self.rrc_info_collector.reset()
        for key in self.featuredict:
            self.featuredict[key] = 0
    
    def reset_intensive_L(self):
        if self.mode == 'intensive':
            self.lte_ss_L =[] # (time, dict)
            self.nr_ss_L = [] # (time, dict)
            self.rrc_L = [] # (time, dict)
        
    def gather_intensive_L(self):
        for _, d in self.lte_ss_L:
            self.lte_ss_collector.SS_DICT += d     
        for _, d in self.nr_ss_L:
            self.nr_ss_collector.SS_DICT += d
        for _, d in self.rrc_L:
            self.rrc_info_collector.RRC_DICT = Rrc_Information_Collector.add_df(self.rrc_info_collector.RRC_DICT, d)

    def remove_intensive_L_by_time(self, time_limit):
        self.lte_ss_L = [(t,d) for t,d in self.lte_ss_L if t > time_limit]
        self.nr_ss_L = [(t,d) for t,d in self.nr_ss_L if t > time_limit]
        self.rrc_L = [(t,d) for t,d in self.rrc_L if t > time_limit]
    
    def get_featuredict(self):
        return self.featuredict
        
    # For LTE RSRP/RSRQ
    def signal_strength(self, msg):
        if msg.type_id == "LTE_PHY_Connected_Mode_Intra_Freq_Meas":
            msg_dict = dict(msg.data.decode())
            easy_dict = LteSignalStrengthCollector.catch_msg(msg_dict)
            if easy_dict['Serving Cell Index'] =='PCell':
                if self.mode == 'default':
                    self.lte_ss_collector.SS_DICT += ss_dict(easy_dict)
                elif self.mode == 'intensive':
                    self.lte_ss_L.append( (dt.datetime.now(), ss_dict(easy_dict)) )
    
    def ss_dict_to_featuredict(self): 

        num_of_nei = len(self.lte_ss_collector.SS_DICT.dict) - 1
        self.featuredict['num_of_neis'], self.features_buffer['num_of_neis'] = num_of_nei, num_of_nei

         # Get primary serv cell rsrp, rsrq 
        if len(self.lte_ss_collector.SS_DICT.dict["PCell"][0]) != 0:
            pcell_rsrp = sum(self.lte_ss_collector.SS_DICT.dict["PCell"][0])/len(self.lte_ss_collector.SS_DICT.dict["PCell"][0])
            pcell_rsrq = sum(self.lte_ss_collector.SS_DICT.dict["PCell"][1])/len(self.lte_ss_collector.SS_DICT.dict["PCell"][0])
        else:
            pcell_rsrp, pcell_rsrq = self.features_buffer['RSRP'], self.features_buffer['RSRQ'] # No sample value, use the previous one
        self.lte_ss_collector.SS_DICT.dict.pop("PCell") 
        self.featuredict['RSRP'], self.featuredict['RSRQ'] = pcell_rsrp, pcell_rsrq
        self.features_buffer['RSRP'], self.features_buffer['RSRQ'] = pcell_rsrp, pcell_rsrq

        # Get 1st, 2nd neighbor cell rsrp, rsrq
        if len(self.lte_ss_collector.SS_DICT.dict) != 0:
            cell1 = max(self.lte_ss_collector.SS_DICT.dict, key=lambda x:sum(self.lte_ss_collector.SS_DICT.dict[x][0])/len(self.lte_ss_collector.SS_DICT.dict[x][0]))
            cell1_rsrp = sum(self.lte_ss_collector.SS_DICT.dict[cell1][0])/len(self.lte_ss_collector.SS_DICT.dict[cell1][0])
            cell1_rsrq = sum(self.lte_ss_collector.SS_DICT.dict[cell1][1])/len(self.lte_ss_collector.SS_DICT.dict[cell1][0])
            self.lte_ss_collector.SS_DICT.dict.pop(cell1)
        else:
            cell1_rsrp, cell1_rsrq = self.features_buffer['RSRP1'], self.features_buffer['RSRQ1'] # No sample value, use the previous one
        self.featuredict['RSRP1'], self.featuredict['RSRQ1'] = cell1_rsrp, cell1_rsrq

        if len(self.lte_ss_collector.SS_DICT.dict) != 0:
            cell2 = max(self.lte_ss_collector.SS_DICT.dict, key=lambda x:sum(self.lte_ss_collector.SS_DICT.dict[x][0])/len(self.lte_ss_collector.SS_DICT.dict[x][0]))
            cell2_rsrp = sum(self.lte_ss_collector.SS_DICT.dict[cell2][0])/len(self.lte_ss_collector.SS_DICT.dict[cell2][0])
            cell2_rsrq = sum(self.lte_ss_collector.SS_DICT.dict[cell2][1])/len(self.lte_ss_collector.SS_DICT.dict[cell2][0])
            self.lte_ss_collector.SS_DICT.dict.pop(cell2)
        else:
            cell2_rsrp, cell2_rsrq = 0,0 # No sample value, assign 0
        self.featuredict['RSRP2'], self.featuredict['RSRQ2'] = cell2_rsrp, cell2_rsrq

    # For NR RSRP/RSRQ
    def nr_signal_strength(self, msg):
        if msg.type_id == "5G_NR_ML1_Searcher_Measurement_Database_Update_Ext":
            msg_dict = dict(msg.data.decode())
            easy_dict = NrSignalStrengthCollector.catch_msg(msg_dict)
            if self.mode == 'default':
                self.nr_ss_collector.SS_DICT += nr_ss_dict(easy_dict)
            elif self.mode == 'intensive':
                self.nr_ss_L.append( (dt.datetime.now(), nr_ss_dict(easy_dict)) )

    def nr_ss_dict_to_featuredict(self):
        # Get primary secondary serv cell rsrp, rsrq 
        if len(self.nr_ss_collector.SS_DICT.dict["PSCell"][0]) != 0:
            pscell_rsrp = sum(self.nr_ss_collector.SS_DICT.dict["PSCell"][0])/len(self.nr_ss_collector.SS_DICT.dict["PSCell"][0])
            pscell_rsrq = sum(self.nr_ss_collector.SS_DICT.dict["PSCell"][1])/len(self.nr_ss_collector.SS_DICT.dict["PSCell"][0])
        else:
            pscell_rsrp, pscell_rsrq = 0,0 # No nr serving or no sample value assign 0
        self.featuredict['nr-RSRP'], self.featuredict['nr-RSRQ'] = pscell_rsrp, pscell_rsrq
        self.nr_ss_collector.SS_DICT.dict.pop("PSCell") 

        # Get 1st, 2nd neighbor cell rsrp, rsrq
        if len(self.nr_ss_collector.SS_DICT.dict) != 0:
            cell1 = max(self.nr_ss_collector.SS_DICT.dict, key=lambda x:sum(self.nr_ss_collector.SS_DICT.dict[x][0])/len(self.nr_ss_collector.SS_DICT.dict[x][0]))
            cell1_rsrp = sum(self.nr_ss_collector.SS_DICT.dict[cell1][0])/len(self.nr_ss_collector.SS_DICT.dict[cell1][0])
            cell1_rsrq = sum(self.nr_ss_collector.SS_DICT.dict[cell1][1])/len(self.nr_ss_collector.SS_DICT.dict[cell1][0])
            self.nr_ss_collector.SS_DICT.dict.pop(cell1)
        else:
            cell1_rsrp, cell1_rsrq = 0,0 # No sample value, assign 0
        self.featuredict['nr-RSRP1'], self.featuredict['nr-RSRQ1'] = cell1_rsrp, cell1_rsrq

        if len(self.nr_ss_collector.SS_DICT.dict) != 0:
            cell2 = max(self.nr_ss_collector.SS_DICT.dict, key=lambda x:sum(self.nr_ss_collector.SS_DICT.dict[x][0])/len(self.nr_ss_collector.SS_DICT.dict[x][0]))
            cell2_rsrp = sum(self.nr_ss_collector.SS_DICT.dict[cell2][0])/len(self.nr_ss_collector.SS_DICT.dict[cell2][0])
            cell2_rsrq = sum(self.nr_ss_collector.SS_DICT.dict[cell2][1])/len(self.nr_ss_collector.SS_DICT.dict[cell2][0])
            self.nr_ss_collector.SS_DICT.dict.pop(cell2)
        else:
            cell2_rsrp, cell2_rsrq = 0,0 # No sample value, assign 0
        self.featuredict['nr-RSRP2'], self.featuredict['nr-RSRQ2'] = cell2_rsrp, cell2_rsrq

    # Get HO events
    def ho_events(self, msg):
        if msg.type_id == "LTE_RRC_OTA_Packet":
            msg_dict = dict(msg.data.decode())
            easy_dict = self.rrc_info_collector.catch_info(msg_dict)
            self.cell_info['MN'] = easy_dict['PCI'][0]
            self.cell_info['earfcn'] = easy_dict['Freq'][0]
            self.cell_info['band'] = self.earfcn_band_pair[easy_dict['Freq'][0]]
            if self.mode == 'default':
                self.rrc_info_collector.RRC_DICT = Rrc_Information_Collector.add_df(self.rrc_info_collector.RRC_DICT, easy_dict)
            elif self.mode == 'intensive':
                self.rrc_L.append( (dt.datetime.now(), easy_dict) )

    def rrc_dict_to_featuredict(self):
        HOs = Rrc_Information_Collector.parse_mi_ho(self.rrc_info_collector.RRC_DICT)
        for key in HOs:
            self.featuredict[key] = 1 if len(HOs[key]) != 0 else 0
            
        MRs = self.rrc_info_collector.mr_tracer.MeasureReport(self.rrc_info_collector.RRC_DICT)
        for key in MRs:
            if key in ['eventA1', 'eventA2', 'E-UTRAN-eventA3', 'eventA5', 'NR-eventA3', 'eventB1-NR-r15']:
                self.featuredict[key] = 1 if len(MRs[key]) != 0 else 0
    
    def offline_test(self, msg):
        msg_dict = dict(msg.data.decode())
        ts = msg_dict['timestamp']
        try: self.ts
        except: self.ts = ts
        if (ts - self.ts).total_seconds() > 1:
            for k, fea in self.featuredict.items():
                self.offline_test_dict[k].append(fea)
            self.reset()
            self.ts = ts
