from model import (PolicyNet, ValueNet)
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from replay_buffer import Replay_buffer
from OU import OUNoise, ExponentialNoiseScheduler
from args import get_args



class DDPGAgent:
    def __init__(self, args):
        self.args = args
        self.device = args.device
        self.max_action = args.max_action

        # 初始化网络
        self.actor = PolicyNet(args.state_dim, args.action_dim, torch.tensor([0.005, 0.003, 0.002])).to(self.device)
        self.actor_target = PolicyNet(args.state_dim, args.action_dim, torch.tensor([1.0, 10.0, 5.0])).to(self.device)
        self.actor_target.load_state_dict(self.actor.state_dict())

        self.critic = ValueNet(args.state_dim, args.action_dim).to(self.device)
        self.critic_target = ValueNet(args.state_dim, args.action_dim).to(self.device)
        self.critic_target.load_state_dict(self.critic.state_dict())

        # 优化器配置
        self.actor_optim = optim.Adam(self.actor.parameters(), lr=args.actor_lr)
        self.critic_optim = optim.Adam(self.critic.parameters(), lr=args.critic_lr)
        self.actor_params = self.actor.state_dict()
        self.critic_params = self.critic.state_dict()
        # 噪声系统
        self.ou_noise = OUNoise(
            args.action_dim,
            mu=args.ou_mu,
            theta=args.ou_theta,
            sigma=args.ou_sigma,
            dt=args.ou_dt
        )
        self.noise_scheduler = ExponentialNoiseScheduler(
            initial_scale=args.noise_initial,
            final_scale=args.noise_final,
            decay_rate=args.noise_decay
        )

        # 经验回放
        self.replay_buffer = Replay_buffer(max_size=int(1e6))

        # 训练指标追踪
        self.loss_critic = 0.0
        self.loss_actor = 0.0
        self.current_q = 0.0

    def select_action(self, state, exploration=True):
        """带噪声的动作选择（支持各维度独立范围）"""
        state = torch.FloatTensor(state).to(self.device).unsqueeze(0)
        with torch.no_grad():
            action = self.actor(state).cpu().numpy().flatten()

        if exploration:
            noise_scale = self.noise_scheduler.get_scale()  # 标量噪声系数（如0.1）
            # 获取各维度独立动作边界（numpy数组，例如[5.0, 3.0, 2.0]）
            action_bound = self.actor.action_bound.cpu().numpy()
            # 生成噪声：噪声幅度按各维度边界比例缩放
            noise = noise_scale * self.ou_noise.sample().numpy() * action_bound
            action = action + noise
            # 按各维度独立裁剪（利用numpy的广播机制）
            action = np.clip(action, -action_bound, action_bound)

        return action

    def update_networks(self):
        """执行网络更新并返回训练指标"""
        if len(self.replay_buffer.storage) < self.args.batch_size:
            return None

        # 从回放池采样
        states, next_states, actions, rewards, dones = self.replay_buffer.sample(
            self.args.batch_size
        )

        # 转换为张量
        states = torch.FloatTensor(states).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        actions = torch.FloatTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        # Critic网络更新
        with torch.no_grad():
            target_actions = self.actor_target(next_states)
            target_q = self.critic_target(next_states, target_actions)
            target_q = rewards + (1 - dones) * self.args.gamma * target_q

        current_q = self.critic(states, actions)
        critic_loss = nn.MSELoss()(current_q, target_q)

        self.critic_optim.zero_grad()
        critic_loss.backward()
        self.critic_optim.step()

        # Actor网络更新
        actor_actions = self.actor(states)
        actor_loss = -self.critic(states, actor_actions).mean()

        self.actor_optim.zero_grad()
        actor_loss.backward()
        self.actor_optim.step()

        # 软更新目标网络
        self._soft_update(self.actor, self.actor_target)
        self._soft_update(self.critic, self.critic_target)

        # 记录训练指标
        self.loss_critic = critic_loss.item()
        self.loss_actor = actor_loss.item()
        self.current_q = current_q.mean().item()

        return {
            'critic_loss': self.loss_critic,
            'actor_loss': self.loss_actor,
            'q_value': self.current_q
        }

    def _soft_update(self, local_model, target_model):
        """执行软更新"""
        for target_param, local_param in zip(target_model.parameters(), local_model.parameters()):
            target_param.data.copy_(
                self.args.tau * local_param.data + (1.0 - self.args.tau) * target_param.data
            )

    def save_models(self, save_dir="models"):
        import os
        os.makedirs(save_dir, exist_ok=True)

        # 保存当前网络和目标网络（可选）
        torch.save(self.actor.state_dict(), f"{save_dir}/actor.pth")
        torch.save(self.critic.state_dict(), f"{save_dir}/critic.pth")
        torch.save(self.actor_target.state_dict(), f"{save_dir}/actor_target.pth")
        torch.save(self.critic_target.state_dict(), f"{save_dir}/critic_target.pth")

    def load_models(self, save_dir="models"):
        self.actor.load_state_dict(torch.load(f"{save_dir}/actor.pth"))
        self.critic.load_state_dict(torch.load(f"{save_dir}/critic.pth"))
        self.actor_target.load_state_dict(torch.load(f"{save_dir}/actor_target.pth"))
        self.critic_target.load_state_dict(torch.load(f"{save_dir}/critic_target.pth"))