# HOW TO USE (Quectel RM500Q only)   
## Step  
1. use get-all-modem.py to get the current modems device node
2. dial-qmi with the specific network interface


## modem-info.sh  
### Description:  
    Acquire the serving/neighbour cell info from target at command port   
    Loop if add delay -t argument and will auto record  
### Command:  
    [bash] ./modem-info.sh -i [interface] {-t [delay sec]}   
  
## band-setting.sh   
### Description:  
    This script can configure the LTE/NSA_NR band combo via the corresponding AT PORT   
### Command:   
    [bash] ./band-setting.sh -i [interface] -l [LTE band combination] -e [ENDC NR Band combination]  

## get-cdc-wdm-num.sh  

***
    Note: Propretary for target modules with unique USB serial ID.
***
### Description:  
    This script can automatic get the target cdc-wdmX dev and target AT command port.  
    Save the results into temp directory.   
    Filename will be the network interface.   
### Command:   
    [bash] ./get-cdc-wdm-num.sh -i [interface]    

## get-all-modem.py  
### Description:  
    This python script is to get the all quectel RM500Q devices.   
    Process the RM500Q modeules with network interface are quectel0 to quectel3.   
### Command:   
    python3 ./get-all-modem.py    
    python3 ./get-all-modem.py -h for help     

## dial-qmi.sh   
### Description:  
    Dial the target qmi dev and network interface with target APN of internet.  
### Command:   
    [bash] ./dial-qmi.sh -i [interface]  
   
## disconnect-qmi.sh   
### Description:   
    Use with dial-qmi.sh   
### Command:  
    [bash] ./disconnect-qmi.sh -i [interface] 
