'''实现InitialState的导入'''
import os
import time # 计算时间
from comtypes.gen import (STKObjects,
                          STKUtil, AgStkGatorLib)  # 从生成的库中获取STK的相关函数
from comtypes.client import (CreateObject,
                             GetActiveObject, GetEvents, CoGetObject, ShowEvents) # 导入生成和获取物体的库
uiapp = GetActiveObject('STK11.Application')
root = uiapp.Personality2
sc1 = root.CurrentScenario
sc2 = sc1.QueryInterface(STKObjects.IAgScenario)
sat1 = sc1.Children.new(18,'cxy_3_2')
sat2 = sat1.QueryInterface(STKObjects.IAgSatellite)
sat2.SetPropagatorType(STKObjects.ePropagatorTwoBody)
propagator = sat2.Propagator
propagator = propagator.QueryInterface(STKObjects.IAgVePropagatorTwoBody)
initial = propagator.InitialState
orbitepoch = initial.OrbitEpoch
orbitepoch.SetExplicitTime('12 Jan 2025 13:35:04.062693804356968')
set = initial.Representation.AssignCartesian(STKUtil.AgECoordinateSystem.eCoordinateSystemTEMEOfDate, 4501.43481101074 ,
                                             -2516.85340894126 , 4598.42717847316, 3.14381092703812  ,6.85238653259152 , 0.568508968971383)

'''我们每四小时调用一次SOTA duration就设置成4 每次调用就行
'''

