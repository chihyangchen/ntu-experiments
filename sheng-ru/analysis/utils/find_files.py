import os 
import json

# This function input the path of experiment directory and output a list of device directories of the experiment directory.
def find_device_under_exp(exp_dir_path):
    dev_dir_list = sorted([os.path.join(exp_dir_path, d) for d in os.listdir(exp_dir_path) if d.startswith('qc') or d.startswith('sm')])
    return dev_dir_list

def find_trace_under_device(dev_dir_path):
    trace_dir_list = sorted([os.path.join(dev_dir_path, d) for d in os.listdir(dev_dir_path)])
    return trace_dir_list

def return_rrc(trace_dir):
    data = os.path.join(trace_dir, 'data')
    d_list = os.listdir(data)
    rrc = filter(lambda x: x.endswith('rrc.csv'), d_list)
    rrc = os.path.join(data, list(rrc)[0])
    return rrc

def return_ml1(trace_dir):
    data = os.path.join(trace_dir, 'data')
    d_list = os.listdir(data)
    rrc = filter(lambda x: x.endswith('ml1.csv') and not x.endswith('nr_ml1.csv'), d_list)
    rrc = os.path.join(data, list(rrc)[0])
    return rrc

def return_nr_ml1(trace_dir):
    data = os.path.join(trace_dir, 'data')
    d_list = os.listdir(data)
    rrc = filter(lambda x: x.endswith('nr_ml1.csv'), d_list)
    rrc = os.path.join(data, list(rrc)[0])
    return rrc
    

def return_UL(trace_dir):
    data = os.path.join(trace_dir, 'data', 'udp_uplk_loss_latency.csv')
    return data

def return_DL(trace_dir):
    data = os.path.join(trace_dir, 'data', 'udp_dnlk_loss_latency.csv')
    return data

# Convenience instance
class EXPERIMENT():
    def __init__(self, exp_dir_path, settings, type):
        self.path = exp_dir_path
        self.settings = json.loads(settings)
        self.type = type
    def __repr__(self):
        return f'EXP: {self.path} -> {self.settings} | T: {self.type}'
    
def get_EXPs(md_files):
    EXPs = []
    for md_file_path in md_files:

        date_dir_path = os.path.dirname(md_file_path)

        with open(md_file_path) as f:

            exp = f.readline()[:-1]
            settings = f.readline()[:-1]

            while exp != '#endif' and settings:
                if '+' not in exp:
                    E = EXPERIMENT(os.path.join(date_dir_path, exp), settings, exp)
                    EXPs.append(E)
                    exp = f.readline()[:-1]
                    settings = f.readline()[:-1]
                else:
                    folder = exp.split('+')[-1]
                    for exp, settings in zip( exp.split('+') , settings.split('+') ):
                        E = EXPERIMENT(os.path.join(date_dir_path, folder), settings, exp)
                        EXPs.append(E)
                    exp = f.readline()[:-1]
                    settings = f.readline()[:-1]
    return EXPs
