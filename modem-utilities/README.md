#HOW TO USE  
##Quectel RM500Q only   
  
##band-setting.sh   
###Description:  
    This script can configure the LTE/NSA_NR band combo via the corresponding AT PORT   
###Command:   
    [bash] ./band-setting.sh -p [ttyUSB PORT] -l [LTE band combination] -e [ENDC NR Band combination]  

##get-cdc-wdm-num.sh  

***
    Note: Propretary for target modules with unique USB serial ID.
***
###Description:  
    This script can automatic get the target cdc-wdmX dev and target AT command port.  
    Save the results in current directory or manual path with -P argument.   
    Filename will be the network interface.   
###Command:   
    [bash] ./get-cdc-wdm-num.sh -i [interface] {-P [PATH]}   

##get-all-modem.py  
###Description:  
    This python script is to get the all quectel RM500Q devices.   
    Process the RM500Q modeules with network interface are quectel0 to quectel3.   
###Command:   
    python3 ./get-all-modem.py {-P [PATH]}   

##dial-qmi.sh   
###Description:  
    Dial the target qmi interface with target APN   
###Command:   
    [bash] ./dial-qmi.sh -i [interface] -s [APN] {-P [PATH]}
   
##disconnect--qmi.sh   
###Description:   
    Use with dial-qmi.sh   
###Command:  
    [bash] ./disconnect-5g-qmi.sh -i [interface] {-P [PATH]}
