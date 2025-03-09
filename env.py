import os
import time # 计算时间
from comtypes.gen import (STKObjects,
                          STKUtil, AgStkGatorLib)  # 从生成的库中获取STK的相关函数
from comtypes.client import (CreateObject,
                             GetActiveObject, GetEvents, CoGetObject, ShowEvents) # 导入生成和获取物体的库
from Initial_establish import env_reset
from get_tianhe_information import get_tianheposition
from get_Relative_information import get_relative_inf
from Remaining_Fuel import get_Remaining_Fuel
from Sota_automation import SOTASimulation
from gym import spaces
import numpy as np
from reward_compute import EscapeSatelliteReward
from get_name import name_model
class stkenv():
    def __init__(self, T):
        '''
        利用python与env交互建立场景 （先把卫星导入，直接获取场景）
        同时要定义动作空间和状态空间
        T指的是自己定义的逃跑方决策间隔时间
        假设为100s
        '''
        uiapp = GetActiveObject('STK11.application')
        self.root = uiapp.Personality2
        self.sc1 = self.root.CurrentScenario
        self.sc2 = self.sc1.QueryInterface(STKObjects.IAgScenario)
        self.sat1 = self.sc1.Children.Item('Tianhe')
        self.sat2 = self.sat1.QueryInterface(STKObjects.IAgSatellite)
        self.T = T
        print(self.T)
        #self.sat1 = self.sc1.Children.Item('Satellite1')#这个就是操作的卫星

        self.actionspace =spaces.Box(-1e7,1e7,(3,)) #动作
        self.observation_space = spaces.Dict({
            # 自身状态（J2000下笛卡尔坐标系）
            "position": spaces.Box(-1e7, 1e7, (3,)),  # 坐标(x,y,z) 单位：米
            "velocity": spaces.Box(-1e4, 1e4, (3,)),  # 速度(vx,vy,vz) 单位：m/s

            # 任务相关状态
            "fuel_remaining": spaces.Box(0, 500, (1,)),  # 剩余燃料
            'fuel_used':spaces.Box(0, 500, (1,)),  # 每次机动使用燃料
            "target_relative_position": spaces.Dict({
                "sat_44714": spaces.Box(-1e4, 1e4, (3,)),  # 目标1
                "sat_44715": spaces.Box(-1e4, 1e4, (3,)),  # 目标2
                "sat_44716": spaces.Box(-1e4, 1e4, (3,)),  # 目标3
                "sat_44717": spaces.Box(-1e4, 1e4, (3,)),  # 目标4
                "sat_44718": spaces.Box(-1e4, 1e4, (3,)),  # 目标5
                }),
            "target_relative_vec": spaces.Dict({
                "sat_44714": spaces.Box(-1e4, 1e4, (3,)),  # 目标1
                "sat_44715": spaces.Box(-1e4, 1e4, (3,)),  # 目标2
                "sat_44716": spaces.Box(-1e4, 1e4, (3,)),  # 目标3
                "sat_44717": spaces.Box(-1e4, 1e4, (3,)),  # 目标4
                "sat_44718": spaces.Box(-1e4, 1e4, (3,)),  # 目标5
                })
            })
        self.reward = EscapeSatelliteReward()

    def reset(self):
        '''
        场景重置 这里要把用代码建立环境部分的代码搬到这里
        重置后记得建立一次env
         '''
        #直接把场景删除，重新建立场景 但是要重新init() 不太合适 还是删除卫星吧
        self.re = env_reset()
        self.re.delSat()
        self.re.establish()
        self.reward.reset()
        initial_obs,_,_ = self.get_observation( n=1, t_44714=-1,t_44715=-1,t_44716=-1,t_44717=-1,t_44718=-1)
        print(initial_obs)
        #这里要返回初始的state
        flattened_state = []

        # 处理基础的属性（如 "position", "velocity", "fuel_remaining", "fuel_used"）
        flattened_state.extend(initial_obs["position"])  # position
        flattened_state.extend(initial_obs["velocity"])  # velocity
        flattened_state.extend(initial_obs["fuel_remaining"])  # fuel_remaining
        flattened_state.extend(initial_obs["fuel_used"])  # fuel_used

        # 处理 targets_relative_position 和 targets_relative_vec
        for key in initial_obs["target_relative_position"]:
            flattened_state.extend(initial_obs["target_relative_position"][key])
            flattened_state.extend(initial_obs["target_relative_vec"][key])
        return flattened_state

    def step(self, action, n, t1, t2, t3, t4, t5):
        '''
        定义状态更新
        '''
        '''
        在这里n为做决策次数 做决策的时间为 n*T 是T的整数倍
        t1 t2 t3 t4 t5 为记录的上次SOTA变轨的时间
        '''
        self.t0 = n * self.T
        #1.把决策返回给逃跑方，让逃跑方更新路径
        valid,min_to_earth = self.send_action_to_stk(action, n) #看是否有效动作
        if valid == 0:
            return 0,0,0,0,valid
        # 2.获取新观测并转换数据形式
        obs, relative_distance1, relative_vec_magnitude1 = self.get_observation(n+1,t1,t2,t3,t4,t5)
        #print(obs)
        #print(obs,relative_distance1,relative_vec_magnitude1)
       # 3.获取奖励

        relative_position = np.array(list(obs['target_relative_position'].values()))
        #print(relative_position)
        relative_velocities = np.array(list(obs['target_relative_vec'].values()))
        #print(relative_velocities)
        relative_distance = np.array(list(relative_distance1.values()))
        ##print(relative_distance)
        relative_vec_magnitude = np.array(list(relative_vec_magnitude1.values()))
        #print(relative_vec_magnitude)
        fuel_remaining = obs['fuel_remaining']
        #print(fuel_remaining)
        fuel_used = obs['fuel_used']
        #print( fuel_used)
        total_reward, done, info = self.reward.calculate_reward(relative_position, relative_distance, relative_velocities,
                                                            min_to_earth, n*self.T)

        # 在这里把Obs展开
        flattened_state = []

        # 处理基础的属性（如 "position", "velocity", "fuel_remaining", "fuel_used"）
        flattened_state.extend(obs["position"])  # position
        flattened_state.extend(obs["velocity"])  # velocity
        flattened_state.extend(obs["fuel_remaining"])  # fuel_remaining
        flattened_state.extend(obs["fuel_used"])  # fuel_used

        # 处理 targets_relative_position 和 targets_relative_vec
        for key in obs["target_relative_position"]:
            flattened_state.extend(obs["target_relative_position"][key])
            flattened_state.extend(obs["target_relative_vec"][key])

        return flattened_state, total_reward, done, info, valid


    def send_action_to_stk(self, action,  n):
        #要是机动后轨迹不合理 和地球重合，要求重新选择动作，要把刚才做的决策恢复
        #先机动
        propagator = self.sat2.propagator
        driver_mcs = propagator.QueryInterface(AgStkGatorLib.IAgVADriverMCS)
        mcs_segments = driver_mcs.MainSequence
        'T指的是逃跑方做决策的时间间隔'
        #if n!= 1:
        #第一次的时候直接加机动 再加一次传播即可
        #if n!=0:
        counts = mcs_segments.Count
        pro = mcs_segments.Item(counts-2).QueryInterface(AgStkGatorLib.IAgVAMCSPropagate)
        stopcon = pro.StoppingConditions
        stopcon.Item(0).properties.QueryInterface(AgStkGatorLib.IAgVAStoppingCondition).Trip = self.T
        driver_mcs.RunMCS()
        #self.sat2 = self.sat1.QueryInterface(STKObjects.IAgSatellite)
        #propagator = self.sat2.propagator
        #driver_mcs = propagator.QueryInterface(AgStkGatorLib.IAgVADriverMCS)
        #mcs_segments = driver_mcs.MainSequence
        maneuver1 = mcs_segments.Insert(AgStkGatorLib.AgEVASegmentType.eVASegmentTypeManeuver, 'Maneuver1', '-')
        Maneuver1 = maneuver1.QueryInterface(AgStkGatorLib.IAgVAMCSManeuver)
        Maneuver1.SetManeuverType(0) #瞬时机动
        MAneuver1 = Maneuver1.Maneuver
        MAneuver1.UpdateMass = 1 #减小燃料
        MAneuver1.setAttitudeControlType(4) #选这个Thrust vector
        AttitudeControl = MAneuver1.QueryInterface(AgStkGatorLib.IAgVAManeuverImpulsive).AttitudeControl
        AttitudeControl = AttitudeControl.QueryInterface(AgStkGatorLib.IAgVAAttitudeControlImpulsive)
        AttitudeControl = AttitudeControl.QueryInterface(AgStkGatorLib.IAgVAAttitudeControlImpulsiveThrustVector)
        AttitudeControl.ThrustAxesName = 'Satellite VVLH' #坐标类型是VVLH 跟观测类型一样
        v = AttitudeControl.DeltaVVector
        v.AssignCartesian(action[0], action[1], action[2]) #默认速度单位是km 设置的时候注意边界大小
        #再传播
        propagate1 = mcs_segments.Insert(AgStkGatorLib.AgEVASegmentType.eVASegmentTypePropagate, 'propagate1', '-')
        propagate1.PropagatorName = "Earth Point Mass"
        propagate = propagate1.QueryInterface(AgStkGatorLib.IAgVAMCSPropagate)
        if n % 2 == 0:
           propagate1.Properties.Color = 16711680
        propagate.PropagatorName = 'Earth Point Mass'
        StoppingCondition = propagate.StoppingConditions
        bb = StoppingCondition.Item(0)
        dd = bb.Properties
        dd = dd.QueryInterface(AgStkGatorLib.IAgVAStoppingCondition)
        dd.Trip = (43800 - n * self.T)
        driver_mcs.RunMCS()
        # 检测是否轨迹不合理
        dataprovider = self.sat1.DataProviders
        provider = dataprovider.Item('LLA State').QueryInterface(STKObjects.IAgDataProviderGroup).Group
        provider1 = provider.Item('Fixed').QueryInterface(STKObjects.IAgDataProvider)
        provider2 = provider1.QueryInterface(STKObjects.IAgDataPrvTimeVar)
        finite = provider2.ExecElements('12 Jan 2025 00:00:00.000', '13 Jan 2025 00:00:00.000', 600,
                                        ['Alt'])
        k1 = finite.DataSets
        kk1 = k1.ToArray()
        if np.min(kk1) <= 100:
            print('不合理')
            counts = mcs_segments.Count
            #print(counts)
            name1 = name_model(counts-2)
            #print(name1)
            name2 = name_model(counts-3)
            #print(name2)
            mcs_segments.Remove(name1) #删掉新动作
            mcs_segments.Remove(name2) #删掉
            driver_mcs.RunMCS()
            #print(mcs_segments.Count)
            # 上面那个传播时间不用改，
            return False,np.min(kk1)
        else:
            return True, np.min(kk1)



    def get_observation(self,n,t_44714,t_44715,t_44716,t_44717,t_44718):
        new_observer = {}
        relative_distance = {}
        relative_vec_magnitude = {}
        new_observer['target_relative_position'] = {}
        new_observer['target_relative_vec'] = {}
        new_observe_tianhe_pos = get_tianheposition(n).position_get()  # 返回自己的位置
        n_p = np.array(new_observe_tianhe_pos[1:])  # 转换成numpy数据
        new_observer['position'] = n_p
        new_observe_tianhe_v = get_tianheposition(n).v_get()  # 返回自己的速度
        n_v = np.array(new_observe_tianhe_v[1:])
        new_observer['velocity'] = n_v
        all_sat = ['Sat_44714', 'Sat_44715', 'Sat_44716', 'Sat_44717', 'Sat_44718'] # 当我复制新卫星的时候 就不合理了
        all_sat_new = ['w_Sat44714', 'w_Sat44715', 'w_Sat44716', 'w_Sat44717', 'w_Sat44718']
        all_relative = {}

        sat_all = []
        t_all = [t_44714, t_44715, t_44716, t_44717, t_44718]
        for i in range(5):
            if n*self.T < t_all[i]:
                sat_all.append(all_sat_new[i])
            else:
                sat_all.append(all_sat[i])
        print(sat_all)

        for i in range(5):
            all_relative[f'tianhe_to{all_sat[i]}'] , direction,  all_relative[f'v_tianhe_to{all_sat[i]}'], ve =  get_relative_inf(sat_all[i], n).get()
            # 返回相对位置和相对速度
            new_observer[f'target_relative_position'][f'{all_sat[i]}'] = np.array(all_relative[f'tianhe_to{all_sat[i]}'][
                                                                             1:4])
            relative_distance[f'{all_sat[i]}'] = np.array(direction[1])
            new_observer[f'target_relative_vec'][f'{all_sat[i]}'] = np.array(all_relative[f'v_tianhe_to{all_sat[i]}'][
                                                                                  1:4])
            relative_vec_magnitude[f'{all_sat[i]}'] = np.array(ve[1])
        if n==0:
            Fuel = [[0],[2000],[0]]
            new_observer['fuel_remaining'] = np.array(Fuel[1])
            new_observer['fuel_used'] = np.array(Fuel[2])
        else:
           Fuel = get_Remaining_Fuel(n).get()
           new_observer['fuel_remaining'] = np.array([Fuel[1]])
           new_observer['fuel_used'] = np.array([Fuel[2]])
        return new_observer,relative_distance,relative_vec_magnitude

