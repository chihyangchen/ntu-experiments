# For NR RSRP/RSRQ
class NrSignalStrengthCollector():
    def __init__(self):
        self.SS_DICT = nr_ss_dict(d={'PSCell':[[],[]]})

    def reset(self):
        self.SS_DICT = nr_ss_dict(d={'PSCell':[[],[]]})

    @staticmethod
    def catch_msg(msg_dict):
        CCL0 = msg_dict['Component_Carrier List'][0]
        easy_dict = {}
        easy_dict['time'], easy_dict["Serving Cell PCI"] = msg_dict['timestamp'], CCL0['Serving Cell PCI']
        easy_dict['neis'] = CCL0['Cells']
        return easy_dict
           
class nr_ss_dict:
    def __init__(self, easy_dict=None, d=None):
        self.dict = {'PSCell':[[],[]]}
        if easy_dict is not None:
            self.nei_cell(easy_dict)
            self.serv_cell(easy_dict)
        if d is not None:
            self.dict = d
    
    def serv_cell(self, easy_dict):
        self.pscell = easy_dict["Serving Cell PCI"]
        do = False
        for cell in self.dict.keys():
            if self.pscell == cell:
                self.dict["PSCell"][0] += self.dict[cell][0]
                self.dict["PSCell"][1] += self.dict[cell][1]
                do,x = True, cell
                break
        if do:
            self.dict.pop(x)
            
    def nei_cell(self, easy_dict):
        # arfcn = easy_dict["Raster ARFCN"]
        neighbors =  easy_dict["neis"] # Different from pandas csv data
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
        return nr_ss_dict(d=d1)