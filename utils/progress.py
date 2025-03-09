from tqdm import tqdm
import time
import numpy as np


class TrainingProgress:
    def __init__(self, total_episodes, window_size=10):
        """
        Args:
            total_episodes (int): 总训练轮数
            window_size (int): 滑动平均窗口大小
        """
        self.total = total_episodes
        self.window = window_size

        # 初始化进度条
        self.bar = tqdm(total=total_episodes,
                        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
                        dynamic_ncols=True)

        # 性能追踪
        self.start_time = time.time()
        self.recent_rewards = []
        self.losses = []

        # 格式设置
        self.postfix_template = {
            'reward': ('Reward', '{value:.1f}'),
            'avg_reward': ('AvgReward', '{value:.1f}'),
            'critic_loss': ('CLoss', '{value:.3f}'),
            'actor_loss': ('ALoss', '{value:.3f}'),
            'noise': ('Noise', '{value:.3f}'),
            'steps': ('Steps', '{value}')
        }

    def update(self, episode, metrics):
        """更新进度信息

        Args:
            metrics (dict): 包含以下键值：
                - total_reward: 当前episode总奖励
                - critic_loss: critic网络损失
                - actor_loss: actor网络损失
                - noise_scale: 当前噪声系数
                - steps: 当前episode步数
        """
        # 更新滑动窗口
        self.recent_rewards.append(metrics['total_reward'])
        self.losses.append((metrics['critic_loss'], metrics['actor_loss']))

        # 保留窗口大小
        if len(self.recent_rewards) > self.window:
            self.recent_rewards.pop(0)
            self.losses.pop(0)

        # 计算统计量
        avg_reward = np.mean(self.recent_rewards) if self.recent_rewards else 0
        avg_closs = np.mean([l[0] for l in self.losses]) if self.losses else 0
        avg_aloss = np.mean([l[1] for l in self.losses]) if self.losses else 0

        # 构建显示信息
        postfix = {
            'reward': metrics['total_reward'],
            'avg_reward': avg_reward,
            'critic_loss': avg_closs,
            'actor_loss': avg_aloss,
            #'noise': metrics['noise_scale'],
            'steps': metrics['steps']
        }

        # 格式化显示
        formatted = {}
        for key, (name, fmt) in self.postfix_template.items():
            formatted[name] = fmt.format(value=postfix.get(key, 0))

        # 更新进度条
        self.bar.set_postfix(**formatted)
        self.bar.update(1)

        # 预估剩余时间
        elapsed = time.time() - self.start_time
        eps_time = elapsed / (episode + 1)
        remaining = eps_time * (self.total - episode - 1)
        self.bar.set_description(f"ETA: {self.format_time(remaining)}")

    def format_time(self, seconds):
        """将秒转换为易读格式"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds // 60:.0f}m {seconds % 60:.0f}s"
        else:
            return f"{seconds // 3600:.0f}h {seconds % 3600 // 60:.0f}m"

    def close(self):
        """结束进度跟踪"""
        self.bar.close()
        total_time = time.time() - self.start_time
        print(f"\nTraining completed in {self.format_time(total_time)}")
        print(f"Average reward (last {self.window} eps): {np.mean(self.recent_rewards):.1f}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
