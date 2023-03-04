#!/usr/bin/python
# Filename: lte_measurement_analyzer.py
"""
Devise your own analyzer

"""

from .analyzer import *

import datetime as dt
from datetime import datetime
from collections import namedtuple
import copy

class MyAnalyzer(Analyzer):
    """
    An self-defined analyzer
    """

    def __init__(self):

        Analyzer.__init__(self)

        # init packet filters
        self.add_source_callback(self.ue_event_filter)

        self.serv_cell_rsrp = []  # rsrp measurements
        self.serv_cell_rsrq = []  # rsrq measurements
        
        # rrc cloumns
        self.columns = [
            "rrcConnectionRelease",
            "rrcConnectionRequest",

            "lte_targetPhysCellId", ## Handover target.
            "dl-CarrierFreq",
            "lte-rrc.t304",
            "nr_physCellId", ## NR measured target PCI
            "nr-rrc.t304",
            "dualConnectivityPHR: setup (1)",
            
            "rrcConnectionReestablishmentRequest",
            "physCellId", ## Target PCI for rrcConnectionReestablishmentRequest.
            "reestablishmentCause", ## ReestablishmentCause for rrcConnectionReestablishmentRequest.

            "scgFailureInformationNR-r15",
            "failureType-r15", ##Failure cause of scgfailure .
        ]

        # init feature element
        self.SS_DICT = self.ss_dict(d={'PCell':[[],[]]})
        self.NR_SS_DICT = self.nr_ss_dict(d={'PSCell':[[],[]]})
        self.RRC_DICT = {}
        self.init_rrc_dict()

        self.featuredict = {
            'LTE_HO': 0, 'MN_HO': 0, 'SN_setup': 0, 'SN_Rel': 0, 'SN_HO': 0, 'RLF': 0, 'SCG_RLF': 0,
            'RSRP': 0, 'RSRQ': 0, 'RSRP1': 0, 'RSRQ1': 0, 'RSRP2': 0, 'RSRQ2': 0, 
            'nr-RSRP': 0, 'nr-RSRQ': 0, 'nr-RSRP1': 0, 'nr-RSRQ1': 0, 'nr-RSRP2': 0, 'nr-RSRQ2':0
        }
        self.timepoint = dt.datetime.now().replace(microsecond=0)
        self.features_buffer = copy.deepcopy(self.featuredict)

        # for testing
        self.test_num = 0

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
        # self.test(msg)
        self.signal_strength(msg)
        self.nr_signal_strength(msg)
        self.ho_events(msg)
 
    # Unified function

    def to_featuredict(self):
        self.ss_dict_to_featuredict()
        self.nr_ss_dict_to_featuredict()
        self.rrc_dict_to_featuredict()

    def reset(self):
        self.SS_DICT = self.ss_dict(d={'PCell':[[],[]]})
        self.NR_SS_DICT = self.nr_ss_dict(d={'PSCell':[[],[]]})
        self.init_rrc_dict()

    def get_featuredict(self):
        return self.featuredict
        
    # For LTE RSRP/RSRQ
    def signal_strength(self, msg):
        if msg.type_id == "LTE_PHY_Connected_Mode_Intra_Freq_Meas":
            msg_dict = dict(msg.data.decode())
            # Create Imitate pandas data
            _pd_data = self.create_pd_data(msg_dict)
    
            serv_cell_idx = _pd_data['Serving Cell Index']
            if serv_cell_idx=='PCell':
                self.SS_DICT += self.ss_dict(_pd_data)

    def create_pd_data(self, msg_dict):
        _pd_data = {} 
        _pd_data["PCI"], _pd_data["time"] = msg_dict['Serving Physical Cell ID'], msg_dict['timestamp']
        _pd_data["EARFCN"], _pd_data["Serving Cell Index"] = msg_dict['E-ARFCN'], msg_dict['Serving Cell Index']
        _pd_data["RSRP(dBm)"], _pd_data["RSRQ(dB)"] = msg_dict["RSRP(dBm)"], msg_dict["RSRQ(dB)"]
        _pd_data["neis"] = msg_dict['Neighbor Cells']
        return _pd_data

    # Give featuredict lte signal strength imformation from ss_dict accumulated for one seconds
    def ss_dict_to_featuredict(self): 

         # Get primary serv cell rsrp, rsrq 
        if len(self.SS_DICT.dict["PCell"][0]) != 0:
            pcell_rsrp = sum(self.SS_DICT.dict["PCell"][0])/len(self.SS_DICT.dict["PCell"][0])
            pcell_rsrq = sum(self.SS_DICT.dict["PCell"][1])/len(self.SS_DICT.dict["PCell"][0])
        else:
            pcell_rsrp, pcell_rsrq = self.features_buffer['RSRP'], self.features_buffer['RSRQ'] # No sample value, use the previous one
        self.SS_DICT.dict.pop("PCell") 
        self.featuredict['RSRP'], self.featuredict['RSRQ'] = pcell_rsrp, pcell_rsrq
        self.features_buffer['RSRP'], self.features_buffer['RSRQ'] = pcell_rsrp, pcell_rsrq

        # Get 1st, 2nd neighbor cell rsrp, rsrq
        if len(self.SS_DICT.dict) != 0:
            cell1 = max(self.SS_DICT.dict, key=lambda x:sum(self.SS_DICT.dict[x][0])/len(self.SS_DICT.dict[x][0]))
            cell1_rsrp = sum(self.SS_DICT.dict[cell1][0])/len(self.SS_DICT.dict[cell1][0])
            cell1_rsrq = sum(self.SS_DICT.dict[cell1][1])/len(self.SS_DICT.dict[cell1][0])
            self.SS_DICT.dict.pop(cell1)
        else:
            cell1_rsrp, cell1_rsrq = 0,0 # No sample value, assign 0
        self.featuredict['RSRP1'], self.featuredict['RSRQ1'] = cell1_rsrp, cell1_rsrq

        if len(self.SS_DICT.dict) != 0:
            cell2 = max(self.SS_DICT.dict, key=lambda x:sum(self.SS_DICT.dict[x][0])/len(self.SS_DICT.dict[x][0]))
            cell2_rsrp = sum(self.SS_DICT.dict[cell2][0])/len(self.SS_DICT.dict[cell2][0])
            cell2_rsrq = sum(self.SS_DICT.dict[cell2][1])/len(self.SS_DICT.dict[cell2][0])
            self.SS_DICT.dict.pop(cell2)
        else:
            cell2_rsrp, cell2_rsrq = 0,0 # No sample value, assign 0
        self.featuredict['RSRP2'], self.featuredict['RSRQ2'] = cell2_rsrp, cell2_rsrq

    # For NR RSRP/RSRQ
    def nr_signal_strength(self, msg):
        if msg.type_id == "5G_NR_ML1_Searcher_Measurement_Database_Update_Ext":
            msg_dict = dict(msg.data.decode())
            _pd_data = self.create_pd_data_nr(msg_dict)
            self.NR_SS_DICT += self.nr_ss_dict(_pd_data)

    def create_pd_data_nr(self, msg_dict):
        CCL0 = msg_dict['Component_Carrier List'][0]
        _pd_data = {}
        _pd_data['time'], _pd_data["Serving Cell PCI"] = msg_dict['timestamp'], CCL0['Serving Cell PCI']
        _pd_data['neis'] = CCL0['Cells']
        return _pd_data

    def nr_ss_dict_to_featuredict(self):
        # Get primary secondary serv cell rsrp, rsrq 
        if len(self.NR_SS_DICT.dict["PSCell"][0]) != 0:
            pscell_rsrp = sum(self.NR_SS_DICT.dict["PSCell"][0])/len(self.NR_SS_DICT.dict["PSCell"][0])
            pscell_rsrq = sum(self.NR_SS_DICT.dict["PSCell"][1])/len(self.NR_SS_DICT.dict["PSCell"][0])
        else:
            pscell_rsrp, pscell_rsrq = 0,0 # No nr serving or no sample value assign 0
        self.featuredict['nr-RSRP'], self.featuredict['nr-RSRQ'] = pscell_rsrp, pscell_rsrq
        self.NR_SS_DICT.dict.pop("PSCell") 

        # Get 1st, 2nd neighbor cell rsrp, rsrq
        if len(self.NR_SS_DICT.dict) != 0:
            cell1 = max(self.NR_SS_DICT.dict, key=lambda x:sum(self.NR_SS_DICT.dict[x][0])/len(self.NR_SS_DICT.dict[x][0]))
            cell1_rsrp = sum(self.NR_SS_DICT.dict[cell1][0])/len(self.NR_SS_DICT.dict[cell1][0])
            cell1_rsrq = sum(self.NR_SS_DICT.dict[cell1][1])/len(self.NR_SS_DICT.dict[cell1][0])
            self.NR_SS_DICT.dict.pop(cell1)
        else:
            cell1_rsrp, cell1_rsrq = 0,0 # No sample value, assign 0
        self.featuredict['nr-RSRP1'], self.featuredict['nr-RSRQ1'] = cell1_rsrp, cell1_rsrq

        if len(self.NR_SS_DICT.dict) != 0:
            cell2 = max(self.NR_SS_DICT.dict, key=lambda x:sum(self.NR_SS_DICT.dict[x][0])/len(self.NR_SS_DICT.dict[x][0]))
            cell2_rsrp = sum(self.NR_SS_DICT.dict[cell2][0])/len(self.NR_SS_DICT.dict[cell2][0])
            cell2_rsrq = sum(self.NR_SS_DICT.dict[cell2][1])/len(self.NR_SS_DICT.dict[cell2][0])
            self.NR_SS_DICT.dict.pop(cell2)
        else:
            cell2_rsrp, cell2_rsrq = 0,0 # No sample value, assign 0
        self.featuredict['nr-RSRP2'], self.featuredict['nr-RSRQ2'] = cell2_rsrp, cell2_rsrq

    # Get HO events
    def ho_events(self, msg):
        if msg.type_id == "LTE_RRC_OTA_Packet":
            # data = msg.data.decode()
            msg_dict = dict(msg.data.decode())
            _pd_data = self.create_pd_data_rrc(msg_dict)
            self.RRC_DICT = self.add_pd_data(self.RRC_DICT, _pd_data)

    def init_rrc_dict(self):
        
        for col in self.columns:
            self.RRC_DICT[col] = []

    def read_rrc_msg_content(self, readlines: list):
        def get_text(l, NAME): ## Given l, return XXXX if NAME in l, else it will error, with format "NAME: XXXX".
            a = l.index('"' + NAME)
            k = len(NAME)+3
            b = l.index("\"", a+1)
            return l[a+k:b]

        def passlines(n):
            nonlocal count, l, readlines
            count += n
            l = readlines[count]

        type_list = [
            "\"rrcConnectionRelease\"",
            "\"lte-rrc.rrcConnectionRequest_element\"",

            "\"lte-rrc.targetPhysCellId\"",
            "dl-CarrierFreq",
            "\"lte-rrc.t304\"",
            "\"nr-rrc.physCellId\"",
            "\"nr-rrc.t304\"",
            "\"dualConnectivityPHR: setup (1)\"",

            "\"rrcConnectionReestablishmentRequest\"",
            "physCellId", 
            "reestablishmentCause",

            "\"scgFailureInformationNR-r15\"",
            "failureType-r15",
        ]  

        type_code = ["0"] * len(type_list)
        l, count = readlines[0], 0
        while count < len(readlines):
            l = readlines[count]
            next = 0
            for i, type in enumerate(type_list):
                if next != 0:
                    next -= 1
                    continue

                c = i
                if type in l and type == "\"lte-rrc.targetPhysCellId\"":
                    type_code[c] = get_text(l, "targetPhysCellId")
                    c += 1
                    passlines(2)
                    if "\"lte-rrc.t304\"" in l:
                        type_code[c] = 'intrafreq'
                        c += 1
                        type_code[c] = "1"
                        next = 2
                    else:
                        passlines(1)
                        type_code[c] = get_text(l, "dl-CarrierFreq")
                        next = 1

                elif type in l and type == "\"nr-rrc.physCellId\"":
                    type_code[c] = get_text(l, "physCellId")

                elif type in l and type == "\"rrcConnectionReestablishmentRequest\"":
                    type_code[c] = "1"
                    c += 1
                    passlines(6)
                    type_code[c] = get_text(l, "physCellId")
                    c += 1 
                    passlines(4)
                    type_code[c] = get_text(l, "reestablishmentCause")
                    next = 2

                elif type in l and type == "\"scgFailureInformationNR-r15\"":
                    type_code[c] = "1"
                    c += 1
                    passlines(13)
                    type_code[c] = get_text(l, "failureType-r15")
                    next = 1
            
                elif type in l and type not in ["physCellId", "dl-CarrierFreq"]:
                    type_code[c] = "1"

            count += 1

        _pd_data = {}
        for type, value in zip(self.columns, type_code):
            _pd_data[type] = value

        return _pd_data

    def create_pd_data_rrc(self, msg_dict):
        _pd_data = {}
        _pd_data["PCI"], _pd_data["time"], _pd_data["Freq"] = msg_dict['Physical Cell ID'], msg_dict['timestamp'], msg_dict['Freq']
        readlines = msg_dict['Msg'].split('\n')
        x = self.read_rrc_msg_content(readlines)
        for key in x:
            _pd_data[key] = x[key]
        for key in _pd_data.keys():
            _pd_data[key] = [str(_pd_data[key])]
        return _pd_data

    def add_pd_data(self, pd_data1, pd_data2):
        d1 = pd_data1
        d2 = pd_data2
        for key in list(d2.keys()):
            if key in list(d1.keys()):
                d1[key] = d1[key] + d2[key]
            else:
                d1[key] = d2[key]
        return d1

    def rrc_dict_to_featuredict(self):
        HOs = self.parse_mi_ho(self.RRC_DICT)
        for key in HOs:
            self.featuredict[key] += len(HOs[key])

    # For testing
    def test(self, msg):
        if msg.type_id == "LTE_PHY_Connected_Mode_Intra_Freq_Meas":
            
            msg_dict = dict(msg.data.decode())
            date = msg_dict['timestamp']
            d = date.replace(microsecond=0)
            print(d)

    class ss_dict:
        def __init__(self,pd_data=None,d=None): ## Input pd_df.iloc[index]
            self.dict = {'PCell':[[],[]]}
            if pd_data is not None:
                self.nei_cell(pd_data)
                self.serv_cell(pd_data)
            if d is not None:
                self.dict = d
        def serv_cell(self, pd_data):
            earfcn = str(pd_data["EARFCN"])
            serv_cell_id = pd_data["Serving Cell Index"]
            pci = str(pd_data["PCI"])
            rsrp = float(pd_data["RSRP(dBm)"])
            rsrq = float(pd_data["RSRQ(dB)"])
            if serv_cell_id == "PCell":
                self.dict['PCell'][0].append(rsrp)
                self.dict['PCell'][1].append(rsrq)
                # self.dict[pci+' '+earfcn] = [[rsrp], [rsrq]]
            else:
                self.dict[pci+' '+earfcn] = [[rsrp], [rsrq]]
                # s = pci + ' ' + self.earfcn
        
        def nei_cell(self, pd_data):
            earfcn = str(pd_data["EARFCN"])
            neighbors = pd_data["neis"] # Different from pandas csv data
            if neighbors is not None:
                for n in neighbors:
                    rsrp = float(n['RSRP(dBm)'])
                    rsrq = float(n['RSRQ(dB)'])
                    pci = str(n['Physical Cell ID'])
                    self.dict[pci+' '+earfcn] = [[rsrp], [rsrq]]              
        
        def __add__(self, sd2):
            d1 = self.dict
            d2 = sd2.dict
            for key in list(d2.keys()):
                if key in list(d1.keys()):
                    d1[key][0] = d1[key][0] + d2[key][0]
                    d1[key][1] += d2[key][1]
                else:
                    d1[key] = d2[key]
            return MyAnalyzer.ss_dict(d=d1)
        
        def __repr__(self):
            return str(self.dict)

    class nr_ss_dict:
        def __init__(self, pd_data=None, d=None):
            self.dict = {'PSCell':[[],[]]}
            if pd_data is not None:
                self.nei_cell(pd_data)
                self.serv_cell(pd_data)
            if d is not None:
                self.dict = d
        
        def serv_cell(self, pd_data):
            self.pscell = pd_data["Serving Cell PCI"]
            do = False
            for cell in self.dict.keys():
                if self.pscell == cell:
                    self.dict["PSCell"][0] += self.dict[cell][0]
                    self.dict["PSCell"][1] += self.dict[cell][1]
                    do,x = True, cell
                    break
            if do:
                self.dict.pop(x)
                
        def nei_cell(self, pd_data):
            # arfcn = pd_data["Raster ARFCN"]
            neighbors =  pd_data["neis"] # Different from pandas csv data
            if neighbors is not None:
                for n in neighbors:
                    rsrp = float(n['Cell Quality Rsrp'])
                    rsrq = float(n['Cell Quality Rsrq'])
                    self.dict[n['PCI']] = [[rsrp], [rsrq]]

        def __repr__(self):
            return str(self.dict)

        def __add__(self, sd2):
            d1 = self.dict
            d2 = sd2.dict
            for key in list(d2.keys()):
                if key in list(d1.keys()):
                    d1[key][0] += d2[key][0]
                    d1[key][1] += d2[key][1]
                else:
                    d1[key] = d2[key]
            return MyAnalyzer.nr_ss_dict(d=d1)
        
    def parse_mi_ho(self, df):
        # HO = namedtuple('HO','start, end, others', defaults=(None,None))
        HO = namedtuple('HO','start', defaults=(None))

        D = {
            'LTE_HO': [], # LTE -> newLTE
            'MN_HO': [], # LTE + NR -> newLTE + NR
            'SN_setup': [], # LTE -> LTE + NR => NR setup
            'SN_Rel': [], # LTE + NR -> LTE
            'SN_HO': [], # LTE + NR -> LTE + newNR
            'RLF': [],
            'SCG_RLF': [],
            }

        for i in range(len(df['rrcConnectionRelease'])):
            t = df["time"][i]
            
            if df["lte-rrc.t304"][i] == '1':
                serv_cell, target_cell = df["PCI"][i], df['lte_targetPhysCellId'][i]
                serv_freq, target_freq = df["Freq"][i], df['dl-CarrierFreq'][i]
                
                if df["nr-rrc.t304"][i] == '1' and df["dualConnectivityPHR: setup (1)"][i] == '1':
                    if serv_cell == target_cell and serv_freq == target_freq:
                        D['SN_setup'].append(HO(start=t))
                        # print(1, t, f"Serving Cell: {serv_cell}->{target_cell}")  
                    else:    
                        D['MN_HO'].append(HO(start=t))
                else:
                    if serv_cell == target_cell and serv_freq == target_freq:
                        D['SN_Rel'].append(HO(start=t))
                    else:
                        D['LTE_HO'].append(HO(start=t))

            if df["nr-rrc.t304"][i] == '1' and not df["dualConnectivityPHR: setup (1)"][i] == '1':
                D['SN_HO'].append(HO(start=t))

            if df["rrcConnectionReestablishmentRequest"][i] == '1':  
                D['RLF'].append(HO(start=t))
                
            if df["scgFailureInformationNR-r15"][i] == '1':
                D['SCG_RLF'].append(HO(start=t))
        
        return D