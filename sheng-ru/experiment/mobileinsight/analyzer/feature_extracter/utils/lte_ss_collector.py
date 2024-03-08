class LteSignalStrengthCollector():
                        
    def __init__(self):
        self.SS_DICT = ss_dict(d={'PCell':[[],[]]})

    def reset(self):
        self.SS_DICT = ss_dict(d={'PCell':[[],[]]})
        
    @staticmethod
    def catch_msg(msg_dict):
        easy_dict = {} 
        easy_dict["PCI"], easy_dict["time"] = msg_dict['Serving Physical Cell ID'], msg_dict['timestamp']
        easy_dict["EARFCN"], easy_dict["Serving Cell Index"] = msg_dict['E-ARFCN'], msg_dict['Serving Cell Index']
        easy_dict["RSRP(dBm)"], easy_dict["RSRQ(dB)"] = msg_dict["RSRP(dBm)"], msg_dict["RSRQ(dB)"]
        easy_dict["neis"] = msg_dict['Neighbor Cells']
        return easy_dict
    
class ss_dict:
        def __init__(self,easy_dict=None,d=None):
            self.dict = {'PCell':[[],[]]}
            if easy_dict is not None:
                self.nei_cell(easy_dict)
                self.serv_cell(easy_dict)
            if d is not None: # use dict to initialize
                self.dict = d
        def serv_cell(self, easy_dict):
            earfcn = str(easy_dict["EARFCN"])
            serv_cell_id = easy_dict["Serving Cell Index"]
            pci = str(easy_dict["PCI"])
            rsrp = float(easy_dict["RSRP(dBm)"])
            rsrq = float(easy_dict["RSRQ(dB)"])
            if serv_cell_id == "PCell":
                self.dict['PCell'][0].append(rsrp)
                self.dict['PCell'][1].append(rsrq)
                # self.dict[pci+' '+earfcn] = [[rsrp], [rsrq]]
            else:
                self.dict[pci+' '+earfcn] = [[rsrp], [rsrq]]
                # s = pci + ' ' + self.earfcn
        
        def nei_cell(self, easy_dict):
            earfcn = str(easy_dict["EARFCN"])
            neighbors = easy_dict["neis"]
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
            return ss_dict(d=d1)
        
        def __repr__(self):
            return str(self.dict)