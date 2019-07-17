import threading
import PyLidar3
# import matplotlib.pyplot as plt
import math    
import time
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui


port =  ("COM10") #windows, cara langsung
Obj = PyLidar3.YdLidarX4(port)
window=pg.plot(title="VFH+")
x1= []       # mendeklarasikan bahwa x adalah list, x adalah sudut dalam radian
y1= []       # y adalah jarak (radius)
prim = []
binA= []
binB= []
binB1= []
binC= []
mask= []
a_index= []
b_index= []
index= []
finalHis= []
plot_keluaran= []
jarak= []
binA_plot= []
binB_plot= []
binC_plot= []
primaryThreshold = 3000
Tmax = 2200
Tmin = 2000
rs = 50 #radius putar maksimal;   2000,satuan cm
ws = 60 #radius aman robot;       1000
sektorTreshold = 10 #jika bukaan dibawah 10 derajat maka dianggap sempit
u1 = 10 #sudut sekarang - sudur target
u2 = 3 #sudut sekarang (mengarahkan ke posisi lurus atau 0)
u3 = 3 #sudut sekarang - sudut sebelumnya
target = 180
target_plot=[]
k_filter = 100
data1 = []




for _ in range(460):
    x1.append(0)
    y1.append(0)
    prim.append(0)
    binA.append(0)
    mask.append(0)
    binB.append(0)
    binB1.append(0)
    binC.append(0)
    a_index.append(0)
    b_index.append(0)
    index.append(0)
    finalHis.append(0)
    plot_keluaran.append(0)
    jarak.append(0)
    binA_plot.append(0)
    binB_plot.append(0)
    binC_plot.append(0)
    target_plot.append(0)
    data1.append(0)
    



def draw():
    if(Obj.Connect()):
        print(Obj.GetDeviceInfo())
        gen = Obj.StartScanning()
        is_plot = True
        keluaran = 180 #180
        kandidat = 0 #0
        while is_plot:
            data = next(gen)
            # Ini buat proses update nilai histogram primary, 
            for angle in range(0,360): #90,271 dan 0,361
                if(data[angle] > 120):                                     #sebelumnya angka 1000, ini radius minimum bacaan, dari datasheet minimum = 0.12m
                    jarak[angle] = data[angle]
                    y1[angle] = data[angle]                            # radius y
                    # x[angle] = (2 * math.pi) - (angle * math.pi / 180)  # dalam radian: untuk plot polar x
                    x1[angle] = angle                              # dalam degree z
                    if -k_filter < data[angle] - data1[angle] < k_filter:
                        prim[angle] = primaryThreshold - (data[angle])# primary histogram
                    else:
                        prim[angle] = 0
                    mask[angle] = data[angle] - (abs(rs*math.sin(math.radians(angle))) + (math.sqrt ((rs*rs)*math.sin(math.radians(angle))*math.sin(math.radians(angle)) + (ws**2) + (2*ws*rs) )))
                    data1[angle] = data[angle]
            # menciptakan binA
            for angle in range(0,360):
                if prim[angle] > Tmax:
                    binA[angle] = 1
                elif prim[angle] < Tmin:
                    binA[angle] = 0
                else :
                    binA[angle] = binA[angle]
            
            # menciptakan binB
            for angle in range(0,360):
                if binA[angle] == 1:
                    if(data[angle] >= ws):
                        if binA[angle] == 1 and binA[angle-1] == 0:
                            a_index[angle] = int(math.degrees(math.asin(ws/data[angle])))
                        else:
                            a_index[angle] = 0
                    elif (120 < data[angle] < ws):
                        a_index[angle] = 0
                else:
                    a_index[angle] = 0
            for angle in range(0,360):
                if binA[angle] == 1:
                    if(data[angle] >= ws):   
                        if binA[angle] == 1 and binA[angle+1] == 0:
                            b_index[angle] = int(math.degrees(math.asin(ws/data[angle])))
                        else:
                            b_index[angle] = 0
                    elif (130 < data[angle] < ws):
                        b_index[angle] = 0
                else:
                    b_index[angle] = 0
            for angle in range(0,360):
                if b_index[angle] > 0:
                    index[angle] = b_index[angle]
                elif a_index[angle] > 0:
                    index[angle] = a_index[angle]
                else:
                    index[angle] = 0
                        # a_index = math.asin(ws/data[angle])
                        # index = int(a_index)
                        # binB1[angle:(angle+1+index)] = [1]*(index+1)
                        # binB1[(angle-1-index):angle] = [1]*(index+1)
            binB[0:361] = [0]*361            
            for angle in range(0,360):
                if binA[angle] == 1:
                    # binB1[angle] = 1
                    if index[angle] > 0:
                        binB[angle:(angle+1+index[angle])] = [1]*(index[angle]+1)
                        binB[(angle-1-index[angle]):angle] = [1]*(index[angle]+1)

            # menciptakan binC (binB + mask)
            a_angleTengah = 180
            a_angleMin = 0
            a_angleMax = 360
            binC[0:361] = [0]*361
            for angle in range(0,361):
                if mask[angle] < 0 :
                    if angle > a_angleTengah:
                        if angle < a_angleMax:
                            a_angleMax = angle
                    else:
                        if angle > a_angleMin:
                            a_angleMin = angle
                angleMin = a_angleMin
                angleMax = a_angleMax
            for angle in range(0,360):
                if angle < angleMin:
                    binC[angle] = 1
                elif angle > angleMax:
                    binC[angle] = 1
            # menciptakan final histogram
            finalHis[0:361] = [0]*361
            for angle in range(0,360):
                if binA[angle] + binB[angle] + binC[angle] > 0:
                    finalHis[angle] = 1
            #mencari kandidat direksi
            nilai_kandidat = 500000000 #jika kandidatnya 5000, maka tidak ada kandidat direksi
            hitung = 0
            for angle in range(0,360):
                if finalHis[angle] == 0 and finalHis[angle-1] == 1: #kasus 1---------------------------------------------------
                    hitung = hitung +1
                    if finalHis[angle + 1] == 1:
                        sudut_kandidat = angle
                        nilai_a = (u1*abs(angle-target))+(u2*abs(angle-180))+(u3*abs(angle-keluaran))
                        # print(nilai_a)
                        if nilai_a < nilai_kandidat:
                            nilai_kandidat = nilai_a
                            kandidat = sudut_kandidat
                            # print(kandidat)
                            hitung = 0
                        else:
                            hitung = 0

                elif finalHis[angle] == 0 and finalHis[angle-1] == 0 and finalHis[angle+1] == 0: #kasus 2----------------------
                    hitung = hitung + 1
                    # print(hitung)

                elif finalHis[angle] == 0 and finalHis[angle+1] == 1: #kasus 3-------------------------------------------------
                    hitung += 1
                    if hitung < sektorTreshold:
                        sudut_kandidat = angle - int(hitung/2)
                        nilai_a = (u1*abs(angle - int(hitung/2)-target))+(u2*abs(angle - int(hitung/2)-180))+(u3*abs(angle - int(hitung/2)-keluaran))
                        # print(nilai_a)
                        if nilai_a < nilai_kandidat:
                            nilai_kandidat = nilai_a
                            kandidat = sudut_kandidat
                            # print(kandidat)
                            hitung = 0
                        else:
                            hitung = 0
                    elif hitung > sektorTreshold:
                        if (angle + 1 - hitung) <= target <= angle:
                            # print((angle + 1 - hitung) , target , angle)
                            # print('yea')
                            if (u1*abs(angle - hitung + 1 - target))+(u2*abs(angle - hitung + 1 -180))+(u3*abs(angle - hitung + 1 - keluaran)) <= (u1*abs(target-target))+(u2*abs(target-180))+(u3*abs(target-keluaran)) and (u1*abs(angle - hitung + 1 - target))+(u2*abs(angle - hitung + 1 -180))+(u3*abs(angle - hitung + 1 - keluaran)) <= (u1*abs(angle-target))+(u2*abs(angle-180))+(u3*abs(angle-keluaran)):
                                sudut_kandidat = angle - hitung + 1
                                nilai_a = (u1*abs(sudut_kandidat-target))+(u2*abs(sudut_kandidat-180))+(u3*abs(sudut_kandidat-keluaran))
                                # print(nilai_a)
                                if nilai_a < nilai_kandidat:
                                    nilai_kandidat = nilai_a
                                    kandidat = sudut_kandidat
                                    # print(kandidat)
                                    hitung = 0
                                else:
                                    hitung = 0
                            elif (u1*abs(target-target))+(u2*abs(target-180))+(u3*abs(target-keluaran)) <= (u1*abs(angle + 1 - hitung-target))+(u2*abs(angle + 1 - hitung-180))+(u3*abs(angle + 1 - hitung-keluaran)) and (u1*abs(target-target))+(u2*abs(target-180))+(u3*abs(target-keluaran)) <= (u1*abs(angle-target))+(u2*abs(angle-180))+(u3*abs(angle-keluaran)):
                                # print('yes')
                                sudut_kandidat = target
                                nilai_a = (u1*abs(sudut_kandidat-target))+(u2*abs(sudut_kandidat-180))+(u3*abs(sudut_kandidat-keluaran))
                                # print(nilai_a)
                                if nilai_a < nilai_kandidat:
                                    nilai_kandidat = nilai_a
                                    kandidat = sudut_kandidat
                                    # print(kandidat)
                                    hitung = 0
                                else:
                                    hitung = 0
                            else:
                                sudut_kandidat = angle
                                nilai_a = (u1*abs(sudut_kandidat-target))+(u2*abs(sudut_kandidat-180))+(u3*abs(sudut_kandidat-keluaran))
                                # print(nilai_a)
                                if nilai_a < nilai_kandidat:
                                    nilai_kandidat = nilai_a
                                    kandidat = sudut_kandidat
                                    # print(kandidat)
                                    hitung = 0
                                else:
                                    hitung = 0
                        else:
                            if (u1*abs(angle-target))+(u2*abs(angle-180))+(u3*abs(angle-keluaran)) <= (u1*abs(angle - hitung + 1-target))+(u2*abs(angle - hitung + 1-180))+(u3*abs(angle - hitung + 1-keluaran)):
                                sudut_kandidat = angle
                                nilai_a = (u1*abs(sudut_kandidat-target))+(u2*abs(sudut_kandidat-180))+(u3*abs(sudut_kandidat-keluaran))
                                # print(nilai_a)
                                if nilai_a < nilai_kandidat:
                                    nilai_kandidat = nilai_a
                                    kandidat = sudut_kandidat
                                    # print(kandidat)
                                    hitung = 0
                                else:
                                    hitung = 0
                            else:
                                sudut_kandidat = angle - hitung + 1
                                nilai_a = (u1*abs(sudut_kandidat-target))+(u2*abs(sudut_kandidat-180))+(u3*abs(sudut_kandidat-keluaran))
                                # print(nilai_a)
                                if nilai_a < nilai_kandidat:
                                    nilai_kandidat = nilai_a
                                    kandidat = sudut_kandidat
                                    # print(kandidat)
                                    hitung = 0
                                else:
                                    hitung = 0
                else:
                    keluaran = 400
                # print(hitung)
                keluaran = kandidat
                # print(keluaran)
            for angle in range(0,402):
                if angle < keluaran-1:
                    plot_keluaran[angle] = 0
                elif angle > keluaran+1:
                    plot_keluaran[angle] = 0
                else:
                    plot_keluaran[angle] = 0.9
            for angle in range(0,402):
                if angle < target-1:
                    target_plot[angle] = 0
                elif angle > target+1:
                    target_plot[angle] = 0
                else:
                    target_plot[angle] = 0.5
            
            for angle in range (0,360):
                if binA[angle] == 1:
                    binA_plot[angle] = 1
                else:
                    binA_plot[angle] = 0
            for angle in range (0,360):
                if binB[angle] == 1:
                    binB_plot[angle] = 1.1
                else:
                    binB_plot[angle] = 0
            for angle in range (0,360):
                if binC[angle] == 1:
                    binC_plot[angle] = 0.8
                else:
                    binC_plot[angle] = 0
            
                
            






threading.Thread(target=draw).start() #jalanin draw dalam thread lain

def update():  
    # bg0a = pg.BarGraphItem(x=x1, height=jarak, width=1, brush='r') 
    # bg0 = pg.BarGraphItem(x=x1, height=prim, width=0.5, brush='c')
    bg1 = pg.BarGraphItem(x=x1, height=binB_plot, width=1, brush='w') # perluasan sudut
    bg2 = pg.BarGraphItem(x=x1, height=binA_plot, width=1, brush='r') # binary A
    bg3 = pg.BarGraphItem(x=x1, height=binC_plot, width=1, brush='y') # batasan steering
    bg4 = pg.BarGraphItem(x=x1, height=plot_keluaran,    width=1, brush='b')
    bg5 = pg.BarGraphItem(x=x1, height=target_plot,    width=1, brush='g')
    window.clear()
    # window.addItem(bg0a)
    # window.addItem(bg0)
    window.addItem(bg1)
    window.addItem(bg2) 
    window.addItem(bg3)
    window.addItem(bg4)
    window.addItem(bg5)
    window.setXRange(50, 300)
    # window.setXRange(0,360)
    window.setYRange(0, 1.1)
    window.plot()





    # window.plot(x1,y1,clear=True)
  

time=QtCore.QTimer()
time.timeout.connect(update)
time.start(25)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
