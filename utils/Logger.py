import os
import csv
import torch
from datetime import datetime
from torch.utils.tensorboard import SummaryWriter


class DDPGLogger:
    def __init__(self, log_dir=None, save_freq=100, track_histograms=True):
        """
        Args:
            log_dir (str): 日志保存路径
            save_freq (int): 模型保存频率（episode）
            track_histograms (bool): 是否记录参数直方图
        """
        # 创建日志目录
        self.log_dir = log_dir or self._create_log_dir()
        os.makedirs(self.log_dir, exist_ok=True)

        # 初始化记录器
        self.writer = SummaryWriter(self.log_dir)
        self.csv_file = os.path.join(self.log_dir, 'training_logs.csv')
        self.model_dir = os.path.join(self.log_dir, 'checkpoints')
        os.makedirs(self.model_dir, exist_ok=True)

        # 配置参数
        self.save_freq = save_freq
        self.track_histograms = track_histograms
        self.episode = 0
        self.metrics_cache = {}

        # 初始化CSV文件头
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'episode', 'total_reward', 'average_q', 'critic_loss',
                'actor_loss', 'noise_scale', 'steps', 'timestamp'
            ])

    def _create_log_dir(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"logs/ddpg_{timestamp}"

    def log_metrics(self, metrics_dict):
        """记录训练指标到TensorBoard和CSV"""
        self.metrics_cache.update(metrics_dict)

        # TensorBoard记录
        self.writer.add_scalar('Main/Total Reward', metrics_dict['total_reward'], self.episode)
        self.writer.add_scalar('Loss/Critic', metrics_dict['critic_loss'], self.episode)
        self.writer.add_scalar('Loss/Actor', metrics_dict['actor_loss'], self.episode)
        self.writer.add_scalar('Params/Noise Scale', metrics_dict['noise_scale'], self.episode)
        self.writer.add_scalar('Params/Q Value', metrics_dict['average_q'], self.episode)

        # 参数直方图记录
        if self.track_histograms and (self.episode % 100 == 0):
            for name, param in metrics_dict['actor_params']:
                self.writer.add_histogram(f"Actor/{name}", param, self.episode)
            for name, param in metrics_dict['critic_params']:
                self.writer.add_histogram(f"Critic/{name}", param, self.episode)

        # CSV记录
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                self.episode,
                metrics_dict['total_reward'],
                metrics_dict['average_q'],
                metrics_dict['critic_loss'],
                metrics_dict['actor_loss'],
                metrics_dict['noise_scale'],
                metrics_dict['steps'],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])

        # 更新episode计数器
        self.episode += 1

    def save_checkpoint(self, agent, episode=None, tag='latest'):
        """保存模型检查点"""
        episode = episode or self.episode
        checkpoint = {
            'actor': agent.actor.state_dict(),
            'critic': agent.critic.state_dict(),
            'episode': episode,
            'optimizer': {
                'actor': agent.actor_optim.state_dict(),
                'critic': agent.critic_optim.state_dict()
            }
        }
        path = os.path.join(self.model_dir, f"checkpoint_{tag}.pth")
        torch.save(checkpoint, path)
        return path

    def close(self):
        """关闭记录器"""
        self.writer.flush()
        self.writer.close()
