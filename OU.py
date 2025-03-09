import numpy as np
import torch


class OUNoise:
    def __init__(self, action_dim, mu=0.0, theta=0.15, sigma=0.2, dt=1e-2):
        """
        Ornstein-Uhlenbeck噪声生成器

        参数说明：
        - action_dim : 动作空间维度
        - mu         : 均值 (默认0.0)
        - theta      : 回归速度参数 (默认0.15)
        - sigma      : 噪声波动率 (默认0.2)
        - dt         : 时间步长 (默认0.01)
        """
        self.mu = mu * np.ones(action_dim)
        self.theta = theta
        self.sigma = sigma
        self.dt = dt
        self.action_dim = action_dim
        self.reset()

    def reset(self):
        """重置噪声状态到初始位置"""
        self.state = np.copy(self.mu)

    def sample(self, scale=1.0):
        """生成噪声样本"""
        dx = self.theta * (self.mu - self.state) * self.dt
        dx += self.sigma * np.sqrt(self.dt) * np.random.randn(self.action_dim)
        self.state += dx
        return torch.from_numpy(scale * self.state).float()


#噪声退火衰减 使用指数退火
#在DDPG算法定义中select_action()中记得让噪声退火
class ExponentialNoiseScheduler:
    def __init__(self, initial_scale=1.0, final_scale=0.1,decay_rate=0.98):
        self.initial = initial_scale
        self.final = final_scale
        self.decay_rate = decay_rate
        self.current = initial_scale

    def get_scale(self):
        self.current = max(self.final, self.current * self.decay_rate)
        return self.current
