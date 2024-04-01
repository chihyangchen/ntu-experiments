# HOW TO USE (Quectel RM500Q only)   
## Step  
1. use get-all-modem.py to get the current modems device node 
2. dial-qmi with the specific network interface
***
note: copy the interface naming file, 70-persistent-net.rules into /etc/udev/rules.d/ to rename the device interface
	  without adding the support of specific module, default name of the network interface for the modules are wwan0,wwan1....
	  set the configuration active: udevadm control --reload-rules && udevadm trigger
***
modem-info to capture the current serving and neighbor cell information.   
band-setting to enable the specific band setting.   
qc-at to send the at command to specific quectel module.  
     
## modem-info.sh  
### Description:  
    Acquire the serving/neighbour cell info from target at command port   
    Loop if add delay -t argument and will auto record 
    delete the looping file in the current directory to stop if running in background.   
### Command:  
    [bash] ./modem-info.sh -i [interface] {-t [delay sec]}   
  
## band-setting.sh   
### Description:  
    This script can configure the LTE/NSA_NR band combo via the corresponding AT PORT  
    Refer the RM500Q documents to see the specific band support. 
    query the current setting: use the -i [interface]  argu. only.   
### Command:   
    [bash] ./band-setting.sh -i [interface] -l [LTE band combination] -e [ENDC NR Band combination]  
    e.g. sudo ./band-setting.sh -i [interface] to query the current setting  
    e.g. sudo ./band-setting.sh -i [interface] -l 1:2:3:4  set the LTE band  
    e.g. sudo ./band-setting.sh -i [interface] -e 77:78:79 set the ENDC NR band   
    e.g. sudo  ./band-setting.sh -i [interface] -l 1:2:3:4  -e 77:78:79 set both LTE and ENDC NR band

## qc-at.sh  
### Description:  
    at command of the specific module
	{TOP} variable of PATH of INTERFACE.lock file
### Command:   
    [bash] qc-at -i [interface] -c [at command]   

## get-cdc-wdm-num.sh  
***
    Note: Propretary for target modules with unique USB serial ID.
***
### Description:  
    This script can automatic get the target cdc-wdmX dev and target DM port.  
    Save the results into temp directory.   
    Filename will be the network interface.   
### Command:   
    [bash] ./get-cdc-wdm-num.sh -i [interface]    

## get-all-modem.py  
### Description:  
    This python script is to get the all quectel RM500Q devices.   
    Process the RM500Q modeules with network interface are qc00 to qc03.   
### Command:   
    [python3] ./get-all-modem.py  

## dial-qmi.sh   
### Description:  
    Dial the target qmi dev and network interface with target APN of "internet".  
### Command:   
    [bash] ./dial-qmi.sh -i [interface]  
   
## disconnect-qmi.sh   
### Description:   
    Use with dial-qmi.sh   
### Command:  
    [bash] ./disconnect-qmi.sh -i [interface]  
## quectel-path.sh   
### Description:   
    func of get specific AT/DM path
