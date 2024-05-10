#!/usr/bin/python
# Filename: lte_measurement_analyzer.py
"""
"""

from mobile_insight.analyzer import *

import datetime


class RlfPredictor(Analyzer):
    """
    An analyzer for LTE radio measurements
    """

    def __init__(self):

        Analyzer.__init__(self)

        # init packet filters
        self.add_source_callback(self.ue_event_filter)

        self.serv_cell_rsrp = []  # rsrp measurements
        self.serv_cell_rsrq = []  # rsrq measurements

    def set_source(self, source):
        """
        Set the source of the trace.
        Enable device's LTE internal logs.

        :param source: the source trace collector
        :param type: trace collector
        """
        Analyzer.set_source(self, source)
        # enable user's internal events
        source.enable_log("LTE_PHY_Connected_Mode_Intra_Freq_Meas")
        source.enable_log("LTE_RRC_OTA_Packet")
        source.enable_log("5G_NR_RRC_OTA_Packet")
        source.enable_log("5G_NR_ML1_Searcher_Measurement_Database_Update_Ext")

    def ue_event_filter(self, msg):
        """
        callback to handle user events

        :param source: the source trace collector
        :param type: trace collector
        """
        # TODO: support more user events
