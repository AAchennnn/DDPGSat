import os
import time # 计算时间
from comtypes.gen import (STKObjects,
                          STKUtil, AgStkGatorLib)  # 从生成的库中获取STK的相关函数
from comtypes.client import (CreateObject,
                             GetActiveObject, GetEvents, CoGetObject, ShowEvents) # 导入生成和获取物体的库

class get_Remaining_Fuel():
    def __init__(self,n):
        self.uiApp = GetActiveObject("STK11.Application")
        # self.uiApp.Visible = True  # 可以看到GUI见面
        # self.uiApp.UserControl = True  # 可以用鼠标和STK GUI交互
        self.stkRoot = self.uiApp.Personality2  # 获取root物体，很重要，所有的物体都是root的子物体
        self.sc1 = self.stkRoot.CurrentScenario
        self.sc2 = self.sc1.QueryInterface(STKObjects.IAgScenario)
        self.sat1 = self.sc1.Children('Tianhe')
        #self.time1 = time1
        self.n = n

    def get(self):
        dataprovider = self.sat1.DataProviders
        provider = dataprovider.Item('Astrogator Values').QueryInterface(STKObjects.IAgDataProviderGroup).Group
        provider1 = provider.Item('Maneuver').QueryInterface(STKObjects.IAgDataProvider)
        provider2 = provider1.QueryInterface(STKObjects.IAgDataPrvTimeVar)
        finite = provider2.ExecElements('12 Jan 2025 00:00:00.000', '13 Jan 2025 00:00:00.000', 600,
                                        ['Time', 'FuelMass', 'Fuel_Used'])
        k = finite.DataSets
        kk = k.ToArray()
        #print(kk)
        #for i in range(k.RowCount):
            #if kk[i][0] == self.time1:
                #print(i)
               # break
        #print(i)
        #print(kk[i])
        return kk[self.n]