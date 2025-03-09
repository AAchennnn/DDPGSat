import os
import time # 计算时间
from comtypes.gen import (STKObjects,
                          STKUtil, AgStkGatorLib)  # 从生成的库中获取STK的相关函数
from comtypes.client import (CreateObject,
                             GetActiveObject, GetEvents, CoGetObject, ShowEvents) # 导入生成和获取物体的库

'''
 输出的是追逐卫星和逃跑卫星之间的相对位置和相对速度
 后续再考虑数据获取的合理性
'''
class get_relative_inf():
    def __init__(self,satellite_name,n):
        self.uiApp = GetActiveObject("STK11.Application")
        # self.uiApp.Visible = True  # 可以看到GUI见面
        # self.uiApp.UserControl = True  # 可以用鼠标和STK GUI交互
        self.stkRoot = self.uiApp.Personality2  # 获取root物体，很重要，所有的物体都是root的子物体
        self.sc1 = self.stkRoot.CurrentScenario
        self.sc2 = self.sc1.QueryInterface(STKObjects.IAgScenario)
        self.sat1 = self.sc1.Children('Tianhe')
        #self.time1 = time1
        self.satellite_name = satellite_name
        self.n = n #第几次观测 从1开始

    def get(self):
        dataprovider = self.sat1.DataProviders
        provider = dataprovider.Item('Vectors(J2000)').QueryInterface(STKObjects.IAgDataProviderGroup).Group
        provider1 = provider.Item(self.satellite_name).QueryInterface(STKObjects.IAgDataProvider)
        provider2 = provider1.QueryInterface(STKObjects.IAgDataPrvTimeVar)
        finite_position_vector = provider2.ExecElements('12 Jan 2025 00:00:00.000', '13 Jan 2025 00:00:00.000', 600,
                                        ['Time', 'x/Magnitude', 'y/Magnitude', 'z/Magnitude'])#, 'Derivative x', 'Derivative y', 'Derivative z', 'Derivative Magnitude'])
        finite_direction = provider2.ExecElements('12 Jan 2025 00:00:00.000', '13 Jan 2025 00:00:00.000', 600, ['Time', 'Magnitude'])
        finite_speed_vector = provider2.ExecElements('12 Jan 2025 00:00:00.000', '13 Jan 2025 00:00:00.000', 600, ['Time', 'Derivative x', 'Derivative y', 'Derivative z'])
        finite_speed = provider2.ExecElements('12 Jan 2025 00:00:00.000', '13 Jan 2025 00:00:00.000', 600, ['Time', 'Derivative Magnitude'])
        #
        k1 = finite_position_vector.DataSets
        kk1 = k1.ToArray()
        #
        k2 = finite_direction.DataSets
        kk2 = k2.ToArray()
        #
        k3 = finite_speed_vector.DataSets
        kk3 = k3.ToArray()
        #
        k4 = finite_speed.DataSets
        kk4 = k4.ToArray()
        #print(kk)
        #for i in range(k1.RowCount):
            #if kk1[i][0] == self.time1:
                #print(i)
                #break
        #print(i)
        #print(kk[i])
        #依次为相对位置向量、相对位置向量大小、相对速度向量、相对速度大小
        return kk1[self.n], kk2[self.n], kk3[self.n], kk4[self.n]