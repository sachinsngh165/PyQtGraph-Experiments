#!/usr/bin/env python3
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph import mkBrush,mkPen,mkColor
from qtGraph import Graph
import numpy as np

# pg.setConfigOption('background', 'w') #to change background to white
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
    
    def draw_net(self):
        pg.setConfigOptions(antialias=True)
        self.w = pg.GraphicsWindow()
        self.w.resize(800,600)
        self.w.setWindowTitle('Overlay Network of the Team')
        self.v = self.w.addViewBox()
        self.v.setAspectLocked()
        self.G = Graph()
        self.v.addItem(self.G)
        self.color_map = {'peer': (169,188,245,255), 'monitor': (169,245,208,255), 'malicious': (247,129,129,255)}

    def update_net(self, node, edge, direction):
        # self.lg.info("Update net", node, edge, direction)
        if node:
            if node[0] == "M" and node[1] == "P":
                if direction == "IN":
                    self.G.add_node(node,self.color_map['malicious'])
                else:
                    self.lg.info("simulator: {} removed from graph (MP)".format(node))
                    self.G.remove_node(node)
            elif node[0] == "M":
                if direction == "IN":
                    self.G.add_node(node,self.color_map['monitor'])
                else:
                    self.G.remove_node(node)
            else:
                if direction == "IN":
                    self.G.add_node(node,self.color_map['peer'])
                else:
                    self.G.remove_node(node)
        else:
            if direction == "IN":
                self.G.add_edge(edge)
            else:
                self.G.add_edge(edge)

    def plot_team(self):
        self.Monitors_rounds = []
        self.WIPs_rounds = []
        self.MPs_rounds = []
        self.Monitors_qty = []
        self.WIPs_qty= []
        self.MPs_qty = []
        self.win = pg.GraphicsWindow(title="Number of Peers in the Team")
        self.win.resize(800,600)

        # Enable antialiasing for prettier plots
        # pg.setConfigOptions(antialias=True)
        self.p3 = self.win.addPlot()
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
            self.lineMPs.setData(self.MPs_rounds,self.MPs_qty)

    def draw_buffer(self):
        self.buff_win = pg.GraphicsWindow(title="Buffer Status")
        self.buff_win.resize(800,700)

        # Enable antialiasing for prettier plots
        # pg.setConfigOptions(antialias=True)

        self.stringaxis = pg.AxisItem(orientation='bottom')
        self.leftaxis = pg.AxisItem(orientation='left')
        self.leftaxis.setTickSpacing(5,1)

        total_peers = self.number_of_monitors + self.number_of_peers + self.number_of_malicious
        self.p4 = self.buff_win.addPlot(axisItems={'bottom': self.stringaxis,'left':self.leftaxis})
        self.p4.showGrid(x=True,y=True,alpha=100)

        self.lineIN = self.p4.plot(pen=(None),name='IN',symbol='o',clear=True)
        # self.lineOUT = self.p4.plot(pen=(None),name='OUT',symbol='o',symbolBrush=mkBrush('#CCCCCC'))

        self.p4.setRange(xRange=[0,total_peers],yRange=[0,self.get_buffer_size()])

        QColors = []
        for ix in range(total_peers):
            color = QtGui.QColor(QtCore.qrand() % 256, QtCore.qrand() % 10, QtCore.qrand() % 256)
            QColors.append(color)

        self.buffer_colors = QColors
        self.buffer_order = {}
        self.buffer_index = 0
        self.buffer_labels = []
        self.grid = np.zeros(shape=(total_peers,self.get_buffer_size()),dtype=int)
        self.grid[:] = -1
        self.colorgrid = np.array([mkColor('#000000')]*(total_peers)*self.get_buffer_size()).reshape(total_peers,self.get_buffer_size())
        self.x = []
        self.y = []
        self.brushes = []

    def update_buffer_round(self, number_of_round):
        self.buff_win.setWindowTitle("Buffer Status " + number_of_round)

    def update_buffer(self, node, senders_shot):
        
        if self.buffer_order.get(node) is None:
            self.buffer_order[node] = self.buffer_index
            self.buffer_labels.append(node)
            xdict = dict(enumerate(self.buffer_labels))
            self.stringaxis.setTicks([xdict.items()])
            text = pg.TextItem()
            text.setText(node)
            text.setColor(self.buffer_colors[self.buffer_index])
            text.setFont(QtGui.QFont("arial", 16))
            text.setPos(self.buffer_index, 1)
            self.p4.addItem(text)
            self.buffer_index += 1

        senders_list = senders_shot.split(":")
        buffer_out = [pos for pos, char in enumerate(senders_list) if char == ""]
        
        for bo in buffer_out:
            self.grid[self.buffer_order[node]][bo] = 0
            self.colorgrid[self.buffer_order[node],bo] = mkColor('#CCCCCC')

        # _x = []
        # _y = []
        # _colors = []

        # for ix in range(self.grid.shape[0]):
        #     for iy in range(self.grid.shape[1]):
        #         if(self.grid[ix,iy]==0):
        #             _x.append(ix) 
        #             _y.append(iy)
        # self.lineOUT.setData(x=_x,y=_y,pen=(None))

        buffer_in = [pos for pos, char in enumerate(senders_list) if char != ""]
        buffer_order_node = self.buffer_order[node]

        color = None
        for pos in buffer_in:
            sender_node = senders_list[pos]
            if sender_node != "S":
                if self.buffer_order.get(sender_node) is not None:
                    color_position = self.buffer_order[sender_node]
                    color = mkColor(self.buffer_colors[color_position])
                else:
                    color = mkColor("#FFFFFF")
            else:
                color = mkColor("#000000")
            self.grid[self.buffer_order[node],pos] = 1
            self.colorgrid[self.buffer_order[node],pos] = color

        _x = []
        _y = []
        _colors = []

        for ix in range(self.grid.shape[0]):
            for iy in range(self.grid.shape[1]):
                if(self.grid[ix,iy]!=-1):
                    _x.append(ix) 
                    _y.append(iy)
                    _colors.append(self.colorgrid[ix,iy])

        self.brushes = [mkBrush(c) for c in _colors]
        self.x = _x
        self.y = _y

        self.lineIN.setData(x=self.x,y=self.y,pen=(None),symbol='o',symbolBrush=self.brushes)
        self.app.processEvents()


    def draw(self):
        self.app = pg.QtGui.QApplication([])
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

        self.draw_net()
        self.plot_team()
        self.draw_buffer()
        time.sleep(1)
        line = drawing_log_file.readline()
        while line != "Bye":
            m = line.strip().split(";", 4)
            if m[0] == "O":
                if m[1] == "Node":
                    if m[2] == "IN":
                        self.update_net(m[3], None, "IN")
                    else:
                        self.update_net(m[3], None, "OUT")
                else:
                    if m[2] == "IN":
                        self.update_net(None, (m[3], m[4]), "IN")
                    else:
                        self.update_net(None, (m[3], m[4]), "OUT")

            if m[0] == "T":
                self.update_team(m[1], m[2], m[3])

            if m[0] == "B":
                self.update_buffer(m[1], m[2])

            self.app.processEvents()
            line = drawing_log_file.readline()





## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fire.Fire(Play)

    logging.shutdown()

