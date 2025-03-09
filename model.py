import torch
import torch.nn as nn
import torch.nn.functional as F

class PolicyNet(nn.Module):
    def __init__(self, state_dim, action_dim,action_bound):
        """
        定义Policy网络结构
        :param state_dim: 状态维度（输入层大小）
        :param action_dim: 动作维度（输出层大小）
        """
        super(PolicyNet, self).__init__()
        self.fc1 = nn.Linear(state_dim, 128)# 第一层全连接：输入层 → 隐藏层1 (128神经元)
        self.fc2 = nn.Linear(128, 128) # 第二层全连接：隐藏层1 → 隐藏层2 (128神经元)
        self.fc3 = nn.Linear(128, action_dim)# 第三层全连接：隐藏层2 → 输出层
        self.tanh = nn.Tanh()

        self.register_buffer('action_bound', torch.as_tensor(action_bound, dtype=torch.float32))
        assert self.action_bound.shape == (action_dim,), "action_bound形状需为[action_dim]"

    def forward(self, state):
        """
        前向传播
        :param state: 输入状态（Tensor）
        :return: 动作（Tensor，范围[-1,1]）
        """
        x = F.relu(self.fc1(state))  # 隐藏层1使用ReLU激活
        x = F.relu(self.fc2(x))  # 隐藏层2使用ReLU激活
        x = self.tanh(self.fc3(x)) * self.action_bound # 输出层使用Tanh
        return x






class ValueNet(nn.Module):
    def __init__(self, state_dim, action_dim):
        """
        定义Value网络结构（Critic）
        :param state_dim: 状态维度（输入层的一部分）
        :param action_dim: 动作维度（输入层的另一部分）
        """
        super(ValueNet, self).__init__()
        self.fc1 = nn.Linear(state_dim + action_dim, 128) # 第一层全连接：状态 + 动作 → 隐藏层1 (128神经元)
        self.fc2 = nn.Linear(128, 128)# 第二层全连接：隐藏层1 → 隐藏层2 (128神经元)
        self.fc3 = nn.Linear(128, 1) # 第三层全连接：隐藏层2 → 输出层（Q值，标量）

    def forward(self, state, action):
        """
        前向传播
        :param state: 输入状态（Tensor，形状 [batch_size, state_dim]）
        :param action: 输入动作（Tensor，形状 [batch_size, action_dim]）
        :return: Q值（Tensor，形状 [batch_size, 1]）
        """
        # 第一步：将状态和动作拼接
        x = torch.cat([state, action], dim=1)  # dim=1表示沿特征维度拼接

        # 全连接层 + 激活函数
        x = F.relu(self.fc1(x))  # 隐藏层1使用ReLU
        x = F.relu(self.fc2(x))  # 隐藏层2使用ReLU
        q_value = self.fc3(x)  # 输出层不激活（Q值可为任意实数）

        return q_value

