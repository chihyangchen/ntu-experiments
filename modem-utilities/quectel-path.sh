#!/bin/bash

function GET_AT_PATH {

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
    m11)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_2559aeac-if03-port0"
        ;;
    m12)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_7444b2b7-if03-port0"
        ;;
    m21)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_98295205-if03-port0"
        ;;
    m22)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_6e8d46d0-if03-port0"
        ;;
    m31)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_48891fdc-if03-port0"
        ;;
    m32)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_86667477-if03-port0"
        ;;
    m41)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_54a942c6-if03-port0"
        ;;
    m42)
        DEV_AT_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_4af8828e-if03-port0"
        ;;

    esac
}

function GET_DM_PATH {
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
    m11)
        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_2559aeac-if00-port0"
        ;;
    m12)
        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_7444b2b7-if00-port0"
        ;;
    m21)
        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_98295205-if00-port0"
        ;;
    m22)
        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_6e8d46d0-if00-port0"
        ;;
    m31)
        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_48891fdc-if00-port0"
        ;;
    m32)
        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_86667477-if00-port0"
        ;;
    m41)
        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_54a942c6-if00-port0"
        ;;
    m42)
        DEV_DM_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_4af8828e-if00-port0"
        ;;

    esac

}

# V3000 use

function GET_GPIO_SLOT {

case "$1" in
		m11)
			SLOT="1"
		;;
		m12)
			SLOT="2"
        ;;
		m21)
			SLOT="1"
        ;;
		m22)
			SLOT="2"
        ;;
		m31)
			SLOT="1"
        ;;
		m32)
			SLOT="2"
        ;;
		m41)
			SLOT="1"
        ;;
		m42)
			SLOT="2"
		;;
	esac

}

#For aceess GPS port
function GET_GPS_PATH {
case "$1" in
    m11)
        DEV_GPS_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_2559aeac-if01-port0"
        ;;
    m12)
        DEV_GPS_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_7444b2b7-if01-port0"
        ;;
    m21)
        DEV_GPS_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_98295205-if01-port0"
        ;;
    m22)
        DEV_GPS_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_6e8d46d0-if01-port0"
        ;;
    m31)
        DEV_GPS_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_48891fdc-if01-port0"
        ;;
    m32)
        DEV_GPS_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_86667477-if01-port0"
        ;;
    m41)
        DEV_GPS_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_54a942c6-if01-port0"
        ;;
    m42)
        DEV_GPS_PATH="/dev/serial/by-id/usb-Quectel_RM500Q-GL_4af8828e-if01-port0"
        ;;

    esac

}

