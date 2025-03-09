import time

from comtypes.gen import (STKObjects,
                          STKUtil, AgStkGatorLib)  # 从生成的库中获取STK的相关函数
from comtypes.client import (CreateObject,
                             GetActiveObject, GetEvents, CoGetObject, ShowEvents) # 导入生成和获取物体的库
from env import stkenv
from Sota_automation import SOTASimulation
from datetime import timedelta
from e_file import e_file_get  #用来搜寻.e文件
from emphasisdata import EphemerisDataExtractor #用来获取新星历的初始信息
import re
class update_chase:
    def __init__(self,k):
        '''k指的更新次数，但是从0开始 因为让追逐方从初始时刻就开始计算 k最大是等于24/duration'''
        self.env = stkenv(600)
        self.root = self.env.root
        self.k = k
        self.sc1 = self.env.sc1
        self.sc2 = self.env.sc2
        Animation = self.sc2.Animation
        Animation.AnimStepValue = 300
        self.animation = self.root.QueryInterface(STKObjects.IAgAnimation)
    def update(self):
        id = 4
        if self.animation.CurrentTime >= 14400 * self.k:
            self.animation.Pause()
            self.animation.CurrentTime = 14400 * self.k
            # 先加上复制星历
            newsatellite = ['w_Sat44714', 'w_Sat44715', 'w_Sat44716', 'w_Sat44717', 'w_Sat44718']
            if self.k != 0:
                for sat in newsatellite:
                    self.sc1.Children.Item(sat).Unload()
            for satellite in ['Sat_44714', 'Sat_44715', 'Sat_44716', 'Sat_44717', 'Sat_44718']:
                self.sc1.Children.Item(satellite).CopyObject(f'w_Sat4471{id}')
                id += 1
            print('此时追逐方做决策', self.animation.CurrentTime)
            SOTA = SOTASimulation()
            SOTA.SOTA_calculate('2025-01-12'
                                , str(timedelta(seconds=14400 * self.k)), 4, f'{self.k}')
            print('决策完毕，更新星历')
            files_all = e_file_get(self.k).get()
            #print(files_all)
            seconds_sat = { }
            for file_path in files_all:
                # 获取初始速度位置 以及epoch
                x, y, z, vx, vy, vz = EphemerisDataExtractor(file_path).extract_initial_position_velocity()
                scenario_epoch, seconds = EphemerisDataExtractor(file_path).extract_scenario_epoch()
                # 获取对应的卫星
                satellite_name = re.search(r'Sat_\d+', file_path).group()
                seconds_sat[f'{satellite_name}'] = seconds
                print(satellite_name)
                sat = self.sc1.Children.Item(satellite_name)
                sat2 = sat.QueryInterface(STKObjects.IAgSatellite)
                sat2.SetPropagatorType(STKObjects.ePropagatorTwoBody)
                propagator = sat2.Propagator
                propagator = propagator.QueryInterface(STKObjects.IAgVePropagatorTwoBody)
                initial = propagator.InitialState
                orbitepoch = initial.OrbitEpoch
                orbitepoch.SetExplicitTime(scenario_epoch)
                set = initial.Representation.AssignCartesian(STKUtil.AgECoordinateSystem.eCoordinateSystemTEMEOfDate,
                                                             x, y, z, vx, vy, vz)
                propagator.propagate()
            return seconds_sat

