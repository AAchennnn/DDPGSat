import time # 计算时间
from comtypes.gen import (STKObjects,
                          STKUtil, AgStkGatorLib)  # 从生成的库中获取STK的相关函数
from comtypes.client import (CreateObject,
                             GetActiveObject, GetEvents, CoGetObject, ShowEvents) # 导入生成和获取物体的库
class env_reset:
    def __init__(self):
        self.uiApp = GetActiveObject("STK11.Application")
        self.uiApp.Visible = True  # 可以看到GUI见面
        self.uiApp.UserControl = True  # 可以用鼠标和STK GUI交互
        self.stkRoot = self.uiApp.Personality2  # 获取root物体，很重要，所有的物体都是root的子物体
        self.sc1 = self.stkRoot.CurrentScenario
        self.sc2 = self.sc1.QueryInterface(STKObjects.IAgScenario)
    def establish(self):
        self.sc2.StartTime = "12 Jan 2025 00:00:00.00"
        self.sc2.StopTime = "12 Jan 2025 13:00:00.00"
        self. stkRoot.Rewind()  # 重置动画到起始时间
        ## 导入初始星历文件
        self.tle_file_path = r"C:\Users\a\Desktop\1_of_starlink.txt"  # 替换为您的 TLE 文件路径
        self.target_ssc_numbers = ["44714", "44715", "44716", "44717", "44718"]  # 目标提取的五颗卫星
        # 如果想提取更多的话 就先把每个TLE数据的第一行提取 储存到ssc_numbers
        for idx, ssc_number in enumerate(self.target_ssc_numbers):  # 从文件中导入这五颗卫星
            # 创建卫星对象
            self.satellite_name = f"Sat_{ssc_number}"  # 动态命名卫星
            self.sat1 = self.sc1.Children.New(18, self.satellite_name)  # 创建卫星
            self.sat2 = self.sat1.QueryInterface(STKObjects.IAgSatellite)
            # 设置传播器为 SGP4
            self.sat2.SetPropagatorType(STKObjects.ePropagatorSGP4)
            self.propagator = self.sat2.Propagator.QueryInterface(STKObjects.IAgVePropagatorSGP4)
            # 设置传播器属性
            self.propagator.Step = 10  # 步长 10 秒
            self.propagator.CommonTasks.AddSegsFromFile(Filename=self.tle_file_path, SSCNumber=ssc_number)  # 导入 TLE 数据
            self.propagator.Propagate()
        # 天宫数据导入
        '''---------------------------------------------天宫数据导入---------------------------------------------------'''
        self.sat1 = self.sc1.Children.New(18, 'Tianhe')
        self.sat2 = self.sat1.QueryInterface(STKObjects.IAgSatellite)
        self.sat2.SetPropagatorType(STKObjects.ePropagatorAstrogator)
        propagator = self.sat2.propagator
        # 获取卫星的 Propagator 对象
        # 查询 IAgVADriverMCS 接口
        driver_mcs = propagator.QueryInterface(AgStkGatorLib.IAgVADriverMCS)
        mcs_segments = driver_mcs.MainSequence
        mcs_segments.RemoveAll()
        # 初始状态定义
        Initial_Orbit = mcs_segments.Insert(AgStkGatorLib.AgEVASegmentType.eVASegmentTypeInitialState, 'Initial ORBIT',
                                            '-')
        InitialState = Initial_Orbit.QueryInterface(AgStkGatorLib.IAgVAMCSInitialState)
        InitialState.FuelTank.MaximumFuelMass = 2000
        InitialState.FuelTank.FuelMass = 2000
        InitialState.SetElementType(AgStkGatorLib.eVAElementTypeCartesian)
        Car = InitialState.Element.QueryInterface(AgStkGatorLib.IAgVAElementCartesian)
        InitialState.OrbitEpoch = "12 Jan 2025 00:00:00.000"
        Car.X = 4590.77
        Car.Y = 4275.63
        Car.Z = 2544.68
        Car.Vx = -2.99863
        Car.Vy = 5.70628
        Car.Vz = -4.16806

        propagate1 = mcs_segments.Insert(AgStkGatorLib.AgEVASegmentType.eVASegmentTypePropagate, 'propagate1', '-')
        propagate1.PropagatorName = "Earth Point Mass"
        propagate = propagate1.QueryInterface(AgStkGatorLib.IAgVAMCSPropagate)
        propagate.PropagatorName = 'Earth Point Mass'
        StoppingCondition = propagate.StoppingConditions
        bb = StoppingCondition.Item(0)
        dd = bb.Properties
        dd = dd.QueryInterface(AgStkGatorLib.IAgVAStoppingCondition)
        dd.Trip = 86400
        driver_mcs.RunMCS()


    def delSat(self):
        for i in range(self.sc1.Children.Count):
            self.sc1.Children.Item(0).Unload()

