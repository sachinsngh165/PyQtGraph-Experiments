#!/usr/bin/env python3
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from qtGraph import Graph



import time
import fire
import logging

class Play():
    
    def __init__(self, drawing_log):
        self.drawing_log = drawing_log

    def get_team_size(self, n):
        return 2 ** (n - 1).bit_length()
        
    def get_buffer_size(self):
        team_size = self.get_team_size((self.number_of_monitors + self.number_of_peers + self.number_of_malicious) * 8)
        if (team_size < 32):
            return 32
        else:
            return team_size 
        
    def plot_team(self):
        self.Monitors_rounds = []
        self.WIPs_rounds = []
        self.MPs_rounds = []
        self.Monitors_qty = []
        self.WIPs_qty= []
        self.MPs_qty = []
        self.win = pg.GraphicsWindow(title="Basic plotting examples")
        self.win.resize(800,600)
        self.win.setWindowTitle('pyqtgraph example: Plotting')

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        self.p3 = self.win.addPlot(title="Drawing with points")
        self.p3.addLegend()
        self.lineWIPs = self.p3.plot(pen=(None), symbolBrush=(0,0,255), symbolPen='b',name='#WIP')
        self.lineMonitors = self.p3.plot(pen=(None), symbolBrush=(0,255,0), symbolPen='g',name='#Monitors Peers')
        self.lineMPs = self.p3.plot( pen=(None), symbolBrush=(255,0,0), symbolPen='r',name='Malicious Peers')

        
        total_peers = self.number_of_monitors + self.number_of_peers + self.number_of_malicious
        self.p3.setRange(xRange=[0,self.number_of_rounds],yRange=[0,total_peers])


    def update_team(self, node, quantity, n_round):
        if node == "M":
            self.Monitors_rounds.append(float(n_round))
            self.Monitors_qty.append(float(quantity))
            self.lineMonitors.setData(self.Monitors_rounds,self.Monitors_qty)
        elif node == "P":
            self.WIPs_rounds.append(float(n_round))
            self.WIPs_qty.append(float(quantity))
            self.lineWIPs.setData(self.WIPs_rounds,self.WIPs_qty)
        else:
            self.MPs_rounds.append(float(n_round))
            self.MPs_qty.append(float(quantity))
            self.lineMPs.setData(self.MPs_rounds,MPs_qty)

        pg.QtGui.QApplication.processEvents()

    def draw(self):
        drawing_log_file = open(self.drawing_log, "r")

        # Read configuration from the first line
        line = drawing_log_file.readline()
        m = line.strip().split(";", 6)
        if m[0] == "C":
            self.number_of_monitors = int(m[1])
            self.number_of_peers = int(m[2])
            self.number_of_malicious = int(m[3])
            self.number_of_rounds = int(m[4])
            self.set_of_rules = m[5]
        else:
            self.lg.info("Invalid format file {}".format(self.drawing_log))
            exit()

        self.plot_team()
        time.sleep(1)
        line = drawing_log_file.readline()
        while line != "Bye":
            m = line.strip().split(";", 4)
            if m[0] == "T":
                self.update_team(m[1], m[2], m[3])
            line = drawing_log_file.readline()




## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fire.Fire(Play)

    logging.shutdown()
