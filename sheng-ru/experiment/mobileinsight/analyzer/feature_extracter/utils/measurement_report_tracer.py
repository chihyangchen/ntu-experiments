from collections import namedtuple
import copy

class REPORTCONFIG:
    def __init__(self, name):
        self.name = name.split(' ')[0]  

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

class MR_Tracer():
    
    def __init__(self):
        self.measobj_dict = {}
        self.report_config_dict = {}
        self.measId_dict = {}
        self.nr_measobj_dict = {}
        self.nr_report_config_dict = {}
        self.nr_measId_dict = {}
    
    
        
    def MeasureReport(self, df):
        MR = namedtuple('MR',['time', 'event'], defaults=[None,None])
        
        types = ['eventA1', 'eventA2', 'E-UTRAN-eventA3', 'eventA5', 'eventA6', 'eventB1-NR-r15',
                 'NR-eventA2', 'NR-eventA3', 
                 'reportCGI', 'reportStrongestCells', 'others']
        D = {k: [] for k in types}
        
        Unknown = REPORTCONFIG('Unknown')
        
        length = len(df['rrcConnectionRelease'])
        for i in range(length):
            time = df['time'][i]
            
            if df["lte-measIdToRemoveList"][i] != '0': pass
            
            if df["lte-measurementReport"][i] == '1':
                id = df['measId'][i]
                try:
                    pairs = self.measId_dict[id] # measObjectId & reportconfigId pairs
                    event = self.report_config_dict[pairs[1]]
                    mr = MR(time=time, event=event)
                except:
                    mr = MR(time=time, event=copy.deepcopy(Unknown))
                
                if 'eventA1' in mr.event.name: D['eventA1'].append(mr)
                elif 'eventA2' in mr.event.name: D['eventA2'].append(mr)  
                elif 'eventA3' in mr.event.name: D['E-UTRAN-eventA3'].append(mr)
                elif 'eventA5' in mr.event.name: D['eventA5'].append(mr)
                elif 'eventA6' in mr.event.name: D['eventA6'].append(mr)  
                elif 'eventB1-NR-r15' in mr.event.name: D['eventB1-NR-r15'].append(mr)
                elif 'reportCGI' in mr.event.name: D['reportCGI'].append(mr)
                elif 'reportStrongestCells' in mr.event.name: D['reportStrongestCells'].append(mr)
                else: D['others'].append(mr)
            
            if df["nr-measurementReport"][i] == '1':
                if not df['measId'][i] == 'none':
                    id = df['measId'][i]
                    try:
                        pairs = self.nr_measId_dict[id] # measObjectId & reportconfigId pairs
                        event = self.nr_report_config_dict[pairs[1]]
                        mr = MR(time=time, event=event)
                    except:
                        mr = MR(time=time, event=copy.deepcopy(Unknown))
                        
                    if 'eventA2' in mr.event.name: D['NR-eventA2'].append(mr)  
                    elif 'eventA3' in mr.event.name: D['NR-eventA3'].append(mr)
                    else: D['others'].append(mr)
            
            if df["lte-MeasObjectToAddMod"][i] == '1':
                Id_list = df["measObjectId"][i].split('@')
                measobj_list = df["measObject"][i].split('@')
                carrierFreq_list = df["carrierFreq"][i].split('@')
                carrierFreq_r15_list = df["carrierFreq-r15"][i].split('@')
                
                for Id, measobj in zip(Id_list, measobj_list):
                    if measobj == "measObjectEUTRA (0)":
                        self.measobj_dict[Id] = MEASOBJ(measobj, carrierFreq_list[0])
                        carrierFreq_list.pop(0)
                    elif measobj == "measObjectNR-r15 (5)":
                        self.measobj_dict[Id] = MEASOBJ(measobj, carrierFreq_r15_list[0])
                        carrierFreq_r15_list.pop(0)
                    
            if df["nr-MeasObjectToAddMod"][i] == '1':
                Id_list = df["measObjectId"][i].split('@')
                measobj_list = df["measObject"][i].split('@')
                ssbFrequency_list = df["ssbFrequency"][i].split('@')

                for Id, measobj in zip(Id_list, measobj_list):
                    if measobj == "measObjectNR (0)":
                        self.nr_measobj_dict[Id] = MEASOBJ(measobj, ssbFrequency_list[0])
                        ssbFrequency_list.pop(0)     
                        
            if df["lte-ReportConfigToAddMod"][i] == '1':
                reportConfigId_list = df["lte-reportConfigId"][i].split('@')
                eventId_list = df["lte-eventId"][i].split('@')
                for Id, eventId in zip(reportConfigId_list, eventId_list):
                    self.report_config_dict[Id] = REPORTCONFIG(eventId)

            if df["nr-ReportConfigToAddMod"][i] == '1':
                reportConfigId_list = df["nr-reportConfigId"][i].split('@')
                eventId_list = df["nr-eventId"][i].split('@')
                for Id, eventId in zip(reportConfigId_list, eventId_list):
                    self.nr_report_config_dict[Id] = REPORTCONFIG(eventId)
            
            if df["lte-MeasIdToAddMod"][i] !=  '0':
                MeasIdToAdd_list = df["lte-MeasIdToAddMod"][i].split('@')
                for group in MeasIdToAdd_list: # measId & measObjectId & reportconfigId 
                    group = MR_Tracer.parse_measIdToAddMod(group)
                    self.measId_dict[group[0]] = (group[1],group[2])

            if df["nr-MeasIdToAddMod"][i] != '0':

                MeasIdToAdd_list = df["nr-MeasIdToAddMod"][i].split('@')
                for group in MeasIdToAdd_list: # measId & measObjectId & reportconfigId 
                    group = MR_Tracer.parse_measIdToAddMod(group)
                    self.nr_measId_dict[group[0]] = (group[1],group[2])
                
        return D
        
    @staticmethod        
    def parse_measIdToAddMod(s):
        a = s.replace('(','')
        a = a.replace(')','')
        a = a.split('&')
        return (a[0], a[1], a[2])
    
    def reset(self):
        self.measobj_dict = {}
        self.report_config_dict = {}
        self.measId_dict = {}
        self.nr_measobj_dict = {}
        self.nr_report_config_dict = {}
        self.nr_measId_dict = {}
        
    