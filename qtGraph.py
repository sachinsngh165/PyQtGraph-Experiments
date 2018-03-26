#!/usr/bin/env python3
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np



class Graph(pg.GraphItem):
    def __init__(self):
        self.textItems = []
        pg.GraphItem.__init__(self)
        self.pos = []
        self.edges = []
        self.texts = []
        
    def setData(self, **kwds):
        self.text = kwds.pop('text', [])
        self.data = kwds
        if 'pos' in self.data:
            npts = self.data['pos'].shape[0]
            self.data['data'] = np.empty(npts, dtype=[('index', int)])
            self.data['data']['index'] = np.arange(npts)
        self.setTexts(self.text)
        self.updateGraph()
        
    def setTexts(self, text):
        for i in self.textItems:
            i.scene().removeItem(i)
        self.textItems = []
        for t in text:
            item = pg.TextItem(t)
            self.textItems.append(item)
            item.setParentItem(self)
        
    def updateGraph(self):
        pg.GraphItem.setData(self, **self.data)
        for i,item in enumerate(self.textItems):
            item.setPos(*self.data['pos'][i])

    def rescale_layout(self,pos,scale=1):
        # rescale to (-scale,scale) in all axes

        # shift origin to (0,0)
        lim=0 # max coordinate for all axes
        for i in range(pos.shape[1]):
            pos[:,i]-=pos[:,i].mean()
            lim=max(pos[:,i].max(),lim)
        # rescale to (-scale,scale) in all directions, preserves aspect
        for i in range(pos.shape[1]):
            pos[:,i]*=scale/lim
        return pos

    def getNodePosn(self,n):
        if n==1:
            return [[0,0]]
        theta = np.linspace(0, 1, n + 1)[:-1] * 2 * np.pi
        theta = theta.astype(np.float32)
        pos = np.column_stack([np.cos(theta), np.sin(theta)])
        pos = self.rescale_layout(pos, scale=1)+(0,0)
        return pos

    def add_node(self,name):
        if name not in self.texts:
            n = len(self.pos)
            self.pos = self.getNodePosn(n+1)
            print(self.pos)
            self.texts.append(name)
            if n>0:
                self.setData(pos=np.array(self.pos,dtype=float), adj=np.array(self.edges,dtype=int),size=0.1, pxMode=False, text=np.array(self.texts))
            print(name + " added ")
    def remove_node(self,n):
        # pass
        self.pos = np.delete(self.pos,n,axis=0)
        self.texts = np.delete(self.texts,n,axis=0)
        print(self.pos.shape)
        for edge in self.edges:
            if edge[0]==n or edge[1]==n:
                self.removeEdge(edge)
                self.setData(pos=np.array(self.pos,dtype=float), adj=np.array(self.edges,dtype=int),size=0.1, pxMode=False, text=np.array(self.texts))
        self.setData(pos=np.array(self.pos,dtype=float), adj=np.array(self.edges,dtype=int),size=0.1, pxMode=False, text=np.array(self.texts))
        print(str(n) + " node removed ")


    def add_edge(self,edge):
        if edge not in self.edges:
            self.edges.append(edge)
            self.setData(pos=np.array(self.pos,dtype=float), adj=np.array(self.edges,dtype=int),size=0.1, pxMode=False, text=np.array(self.texts))

    def removeEdge(self,edge):
        if edge in self.edges:
            self.edges.remove(edge)
            self.setData(pos=np.array(self.pos,dtype=float), adj=np.array(self.edges,dtype=int),size=0.1, pxMode=False, text=np.array(self.texts))



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys,time
        # Enable antialiasing for prettier plots
    app = QtGui.QApplication([])


    pg.setConfigOptions(antialias=True)

    w = pg.GraphicsWindow()
    w.setWindowTitle('pyqtgraph example: CustomGraphItem')
    v = w.addViewBox()
    v.setAspectLocked()
    ## Define positions of nodes


    g = Graph()
    v.addItem(g)
    
    g.add_node('node 0')
    g.add_node('node 1')
    g.add_node('node 2')
    g.add_node('node 3')
    g.add_node('node 4')
    g.add_edge([0,1])
    g.add_edge([1,2])
    g.add_edge([0,2])
    g.add_edge([1,3])
    # g.remove_node(2) 

    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    QtGui.QApplication.instance().exec_()