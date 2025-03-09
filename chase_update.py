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
env = stkenv(100)
root = env.root

sc1 = env.sc1
sc2 = env.sc2
Animation = sc2.Animation
Animation.AnimaStepValue = 100
animation = root.QueryInterface(STKObjects.IAgAnimation)
k = 0
animation.PlayForward()
while(1):
    id = 4
    if animation.CurrentTime >= 14400*k:
        animation.Pause()
        animation.CurrentTime = 14400*k
        #先加上复制星历
        newsatellite= ['w_Sat44714','w_Sat44715','w_Sat44716','w_Sat44717','w_Sat44718']
        if k != 0:
            for sat in newsatellite:
                sc1.Children.Item(sat).Unload()
        for satellite in ['Sat_44714','Sat_44715', 'Sat_44716', 'Sat_44717', 'Sat_44718']:
            sc1.Children.Item(satellite).CopyObject(f'w_Sat4471{id}')
            id += 1
        print('此时追逐方做决策', animation.CurrentTime)
        SOTA = SOTASimulation()
        SOTA.SOTA_calculate('2025-01-12'
                            , str(timedelta(seconds=14400*k)), 4 , f'{k}')
        print('决策完毕，更新星历')
        files_all = e_file_get(k).get()
        print(files_all)
        for file_path in files_all:
            #获取初始速度位置 以及epoch
            x, y, z, vx, vy, vz = EphemerisDataExtractor(file_path).extract_initial_position_velocity()
            scenario_epoch, _ = EphemerisDataExtractor(file_path).extract_scenario_epoch()
            #获取对应的卫星
            satellite_name = re.search(r'Sat_\d+', file_path).group()
            print(satellite_name)
            sat = sc1.Children.Item(satellite_name)
            sat2 = sat.QueryInterface(STKObjects.IAgSatellite)
            sat2.SetPropagatorType(STKObjects.ePropagatorTwoBody)
            propagator = sat2.Propagator
            propagator = propagator.QueryInterface(STKObjects.IAgVePropagatorTwoBody)
            initial = propagator.InitialState
            orbitepoch = initial.OrbitEpoch
            orbitepoch.SetExplicitTime(scenario_epoch)
            set = initial.Representation.AssignCartesian(STKUtil.AgECoordinateSystem.eCoordinateSystemTEMEOfDate,
                                                         x,y,z,vx,vy,vz)
            propagator.propagate()

       # 这里写替换星历 先提取0/1/2....开头的.e文件 找到这个文件名字中对应的卫星
        #然后利用昨天写的emphasisdata把 time、x、y、z v合并成一个 () 然后再用昨天那个Twobody的替换！
        k += 1
        time.sleep(3)
        animation.PlayForward()
    if k == 6:
        break

#这个代码文件作为背景一直跑就行了
#t1 = 400
#t2=200
#t3 = 600
#t4 = 300
#t5 = 200
#ew_observer,relative_distance,relative_vec_magnitude =env.get_observation(2,t1,t2,t3,t4,t5)
#print(ew_observer,relative_distance,relative_vec_magnitude)
#记得成立的条件，是我设置的生成的report的step = T
#env.step([0.3,0.5,0.1],1)
#new_observer,relative_distance,relative_vec_magnitude=env.get_observation(1)
#print('新观测',new_observer)
#print('相对的距离',relative_distance)
#print('相对速度',relative_vec_magnitude)

#现在已经可以开始写训练的代码了
