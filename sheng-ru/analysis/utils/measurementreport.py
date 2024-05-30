import pandas as pd
import datetime as dt
import copy
from collections import namedtuple

class REPORTCONFIG:
    def __init__(self, name, parameter):
        self.name = name.split(' ')[0]  
        self.parameters = self.parse_parameter(parameter)
    
    def parse_parameter(self, parameter):
        L = []
        start = False
        for i in range(len(parameter)):
            if parameter[i] == "'" and start == False:
                s = ''
                start = True
                continue
            
            if start:
                if parameter[i] == "'":
                    L.append(s)
                    start = False
                s += parameter[i]
        
        P = dict()
        filter = '+-0123456789[]()&'
        for i in range(0,len(L),2):
            x = ''
            for c in L[i+1]:
                if c in filter:
                    x += c
            try:
                P[L[i]] = int(x)
            except:
                P[L[i]] = x
        return P
    
    def reset_name(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class MEASOBJ:

    def __init__(self, obj, freq):
        self.name = obj
        self.freq = freq

    def __str__(self):
        return f'({self.name}, {self.freq})'

    def __repr__(self):
        return f'({self.name}, {self.freq})'

def parse_measIdToAddMod(s):
    a = s.replace('(','')
    a = a.replace(')','')
    a = a.split('&')
    return (a[0], a[1], a[2])

MR = namedtuple('MR',['time', 'event', 'others'], defaults=[None,None,''])
def MeasureReport(file):

    mi_rrc_df = pd.read_csv(file)
    mi_rrc_df["Timestamp"] = mi_rrc_df["Timestamp"].swifter.apply(lambda x: pd.to_datetime(x) + dt.timedelta(hours=8))
    unused = ['DL frequency','UL frequency', 'DL bandwidth', 'UL bandwidth', 'Cell Identity', 'TAC','Band ID', 'MCC', 'MNC']
    mi_rrc_df = mi_rrc_df.drop(columns=unused)
    mi_rrc_df = mi_rrc_df.dropna()    
    cols_to_covert = ['measObjectId', 'carrierFreq', 'carrierFreq-r15', 'lte-reportConfigId', 'lte-measIdToRemoveList', 'measId', 'ssbFrequency']
    mi_rrc_df[cols_to_covert] = mi_rrc_df[cols_to_covert].astype('str')

    measobj_dict, report_config_dict, measId_dict = {}, {}, {}
    nr_measobj_dict, nr_report_config_dict, nr_measId_dict = {}, {}, {}

    def reset():

        global measobj_dict, report_config_dict, measId_dict, nr_measobj_dict, nr_report_config_dict, nr_measId_dict  
        measobj_dict, report_config_dict, measId_dict = {}, {}, {}
        nr_measobj_dict, nr_report_config_dict, nr_measId_dict = {}, {}, {}

    L = []

    RRC_connected = True
    Unknown = REPORTCONFIG('Unknown', {})

    for i in range(len(mi_rrc_df)):

        if mi_rrc_df['type_id'].iloc[i] == "5G_NR_RRC_OTA_Packet" or mi_rrc_df['type_id'].iloc[i] == "LTE_RRC_Serv_Cell_Info":
            continue

        time = mi_rrc_df['Timestamp'].iloc[i]
        others = ''
        
        # if mi_rrc_df["rrcConnectionRelease"].iloc[i] == 1:      
        #     reset()

        if mi_rrc_df["lte-measIdToRemoveList"].iloc[i] != '0':

            measIdToRemove_list = mi_rrc_df["lte-measIdToRemoveList"].iloc[i].split('@')
            if len(measIdToRemove_list) == 32:
                measId_dict = {}
            elif len(measId_dict) != 0:
                for a in range(len(measIdToRemove_list)):
                    try: measId_dict.pop(measIdToRemove_list[a])
                    except: pass

        if mi_rrc_df["lte-measurementReport"].iloc[i] == 1:
            
            others += 'E-UTRAN'
            id = str(int(float(mi_rrc_df['measId'].iloc[i])))

            try:
                x = measId_dict[id]
                event = report_config_dict[x[1]]
                mr = MR(time = time, event = event, others = others)
            except:
                mr = MR(time = time, event = copy.deepcopy(Unknown), others = others)

            L.append(mr)

        if mi_rrc_df["nr-measurementReport"].iloc[i] == 1:
            
            others += 'NR'
            id = str(int(float(mi_rrc_df['measId'].iloc[i])))

            try:
                x = nr_measId_dict[id]
                event = nr_report_config_dict[x[1]]
                mr = MR(time = time, event = event, others = others)
            except:
                mr = MR(time = time, event = copy.deepcopy(Unknown), others = others)
            
            L.append(mr)

        if mi_rrc_df["lte-MeasObjectToAddMod"].iloc[i] == 1:

            Id_list = mi_rrc_df["measObjectId"].iloc[i].split('@')
            measobj_list = mi_rrc_df["measObject"].iloc[i].split('@')
            carrierFreq_list = mi_rrc_df["carrierFreq"].iloc[i].split('@')
            carrierFreq_r15_list = mi_rrc_df["carrierFreq-r15"].iloc[i].split('@')
            
            for a in range(len(Id_list)):
                if measobj_list[a] == "measObjectEUTRA (0)":
                    measobj_dict[Id_list[a]] = MEASOBJ(measobj_list[a], carrierFreq_list[0])
                    carrierFreq_list.pop(0)
                elif measobj_list[a] == "measObjectNR-r15 (5)":
                    measobj_dict[Id_list[a]] = MEASOBJ(measobj_list[a], carrierFreq_r15_list[0])
                    carrierFreq_r15_list.pop(0)
    

        if mi_rrc_df["nr-MeasObjectToAddMod"].iloc[i] == 1:

            Id_list = mi_rrc_df["measObjectId"].iloc[i].split('@')
            measobj_list = mi_rrc_df["measObject"].iloc[i].split('@')
            ssbFrequency_list = mi_rrc_df["ssbFrequency"].iloc[i].split('@')

            for a in range(len(Id_list)):
                if measobj_list[a] == "measObjectNR (0)":
                    nr_measobj_dict[Id_list[a]] = MEASOBJ(measobj_list[a], ssbFrequency_list[0])
                    ssbFrequency_list.pop(0)     

            
        if mi_rrc_df["lte-ReportConfigToAddMod"].iloc[i] == 1:

            reportConfigId_list = mi_rrc_df["lte-reportConfigId"].iloc[i].split('@')
            eventId_list = mi_rrc_df["lte-eventId"].iloc[i].split('@')
            parameter_list = mi_rrc_df["lte-parameter"].iloc[i].split('@')
            for a in range(len(reportConfigId_list)):
                report_config_dict[reportConfigId_list[a]] = REPORTCONFIG(eventId_list[a], parameter_list[a])


        if mi_rrc_df["nr-ReportConfigToAddMod"].iloc[i] == 1: #############

            reportConfigId_list = mi_rrc_df["nr-reportConfigId"].iloc[i].split('@')
            eventId_list = mi_rrc_df["nr-eventId"].iloc[i].split('@')
            parameter_list = mi_rrc_df["nr-parameter"].iloc[i].split('@')
            for a in range(len(reportConfigId_list)):
                nr_report_config_dict[reportConfigId_list[a]] = REPORTCONFIG(eventId_list[a], parameter_list[a])

        if mi_rrc_df["lte-MeasIdToAddMod"].iloc[i] != '0':

            MeasIdToAdd_list = mi_rrc_df["lte-MeasIdToAddMod"].iloc[i].split('@')
            for a in range(len(MeasIdToAdd_list)):
                x = parse_measIdToAddMod(MeasIdToAdd_list[a])
                measId_dict[x[0]] = (x[1],x[2])


        if mi_rrc_df["nr-MeasIdToAddMod"].iloc[i] != '0' and mi_rrc_df["nr-MeasIdToAddMod"].iloc[i] != 0:

            MeasIdToAdd_list = mi_rrc_df["nr-MeasIdToAddMod"].iloc[i].split('@')
            for a in range(len(MeasIdToAdd_list)):
                x = parse_measIdToAddMod(MeasIdToAdd_list[a])
                nr_measId_dict[x[0]] = (x[1],x[2])

    # Sort to Dict
    types = ['eventA1','eventA2','E-UTRAN-eventA3', 'eventA5', 'eventA6','NR-eventA3', 'eventB1-NR-r15','reportCGI', 'reportStrongestCells', 'others']
    D = {k: [] for k in types}

    for mr in L:

        if 'E-UTRAN' in mr.others and 'eventA1' in mr.event.name:
            D['eventA1'].append(mr)
        
        elif 'E-UTRAN' in mr.others and 'eventA2' in mr.event.name:
            D['eventA2'].append(mr)  
        
        elif 'E-UTRAN' in mr.others and 'eventA3' in mr.event.name:
            D['E-UTRAN-eventA3'].append(mr)
        
        elif 'E-UTRAN' in mr.others and 'eventA5' in mr.event.name:
            D['eventA5'].append(mr)

        elif 'E-UTRAN' in mr.others and 'eventA6' in mr.event.name:
            D['eventA6'].append(mr)  
        
        elif 'E-UTRAN' in mr.others and 'eventB1-NR-r15' in mr.event.name:
            D['eventB1-NR-r15'].append(mr)
        
        elif 'E-UTRAN' in mr.others and 'reportCGI' in mr.event.name:
            D['reportCGI'].append(mr)
        
        elif 'E-UTRAN' in mr.others and 'reportStrongestCells' in mr.event.name:
            D['reportStrongestCells'].append(mr)
        
        elif 'NR' in mr.others and 'eventA3' in mr.event.name:
            D['NR-eventA3'].append(mr)       
        
        else:
            D['others'].append(mr)

    return D

def map_MR_HO(MRs, HOs):

    map_ho_types = ['LTE_HO', 'MN_HO', 'MN_HO_to_eNB', 'SN_setup', 'SN_Rel', 'SN_HO', ]
    map_mr_types = ['E-UTRAN-eventA3', 'eventA5', 'eventB1-NR-r15', 'NR-eventA3']

    D = {'LTE_HO': [], 'NR_HO': [], 'SN_setup': []}

    for lte_ho_type in ['LTE_HO', 'MN_HO', 'MN_HO_to_eNB']:
        for ho in HOs[lte_ho_type]:
            for mr_type in ['E-UTRAN-eventA3', 'eventA5']:
                
                for mr in MRs[mr_type]:
                    # The current mapping way may map a HO with repeated measurement report.
                    dif = (ho.start - mr.time).total_seconds()
                    if 0 < dif < 0.5:
                        D['LTE_HO'].append((mr, ho, lte_ho_type))

    for nr_ho_type in ['SN_Rel', 'SN_HO']:
        for ho in HOs[nr_ho_type]:
            for mr in MRs['NR-eventA3']:

                dif = (ho.start - mr.time).total_seconds()
                if 0 < dif < 0.5:
                    D['NR_HO'].append((mr, ho, nr_ho_type))

    for ho in HOs['SN_setup']:
        for mr in MRs['eventB1-NR-r15']:

            dif = (ho.start - mr.time).total_seconds()
            if 0 < dif < 0.5:
                D['SN_setup'].append((mr, ho, 'SN_setup'))

    return D 

# Correct MR with HO
def correct_MR_with_HO(MRs, HOs):
    MR = namedtuple('MR',['time', 'event', 'others'], defaults=[None,None,''])
    new_MRs = copy.deepcopy(MRs)
    del new_MRs['others']

    for mr in MRs['others']:
        if 'E-UTRAN' in mr.others:
            for ho in HOs['LTE_HO'] + HOs['MN_HO']:
                if 0.3 > (ho.start - mr.time).total_seconds() > 0:
                    mr.event.reset_name('eventA3')
                    new_MRs['E-UTRAN-eventA3'].append(MR(time = mr.time, event = mr.event, others = mr.others))
    
        elif 'NR' in mr.others:
            for ho in HOs['SN_HO']:
                if 0.3 > (ho.start - mr.time).total_seconds() > 0:
                    mr.event.reset_name('eventA3')
                    new_MRs['NR-eventA3'].append(MR(time = mr.time, event = mr.event, others = mr.others))
    
    return new_MRs                