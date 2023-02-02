#!/bin/bash

GET_AT_PATH(){

case "$1" in
    wwan0)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_7444b2b7-if03-port0"
        ;;
    qc00)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_76857c8-if03-port0"
        ;;
    qc01)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_bc4587d-if03-port0"
        ;;
    qc02)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_5881b62f-if03-port0"
        ;;
    qc03)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_32b2bdb2-if03-port0"
        ;;
    esac
}

GET_DM_PATH(){
case "$1" in
    wwan0)
        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_7444b2b7-if00-port0"
        ;;
    wwan1)
        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_ed1c8b2e-if00-port0"
        ;;
    qc00)
        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_76857c8-if00-port0"
        ;;
    qc01)
        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_bc4587d-if00-port0"
        ;;
    qc02)
        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_5881b62f-if00-port0"
        ;;
    qc03)
        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_32b2bdb2-if00-port0"
        ;;
    esac

}
