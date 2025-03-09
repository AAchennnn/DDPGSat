from tqdm import tqdm
import time


class DDPGProgress:
    def __init__(self, total_episodes, update_interval=10):
        self.total_episodes = total_episodes
        self.update_interval = update_interval
        self.start_time = time.time()

        # 进度条配置
        self.bar_format = "{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        self.progress_bar = tqdm(
            total=total_episodes,
            desc="Training Progress",
            bar_format=self.bar_format,
            dynamic_ncols=True
        )

        # 指标缓存
        self.current_metrics = {
            'reward': 0,
            'critic_loss': 0,
            'noise_scale': 0,
            'steps': 0,
            'epsilon': 1.0
        }

    def update(self, episode, metrics):
        """更新进度显示"""
        # 更新当前指标
        self.current_metrics.update(metrics)

        # 格式化显示信息
        postfix = (
            f"Reward: {metrics['reward']:.1f} | "
            f"Critic Loss: {metrics['critic_loss']:.3f} | "
            f"Noise: {metrics['noise_scale']:.2f} | "
            f"Steps: {metrics['steps']} | "
            f"Epsilon: {metrics['epsilon']:.2f}"
        )

        # 更新进度条
        self.progress_bar.set_postfix_str(postfix)
        self.progress_bar.update(1)

        # 定期刷新完整信息
        if (episode + 1) % self.update_interval == 0:
            self._print_detailed_status(episode)

    def _print_detailed_status(self, episode):
        """打印详细训练状态"""
        elapsed = time.time() - self.start_time
        eps_per_sec = (episode + 1) / elapsed
        remaining = (self.total_episodes - episode - 1) / eps_per_sec

        print(f"\n=== Episode {episode + 1} Status ===")
        print(f"Elapsed: {self._format_time(elapsed)}")
        print(f"Remaining: {self._format_time(remaining)}")
        print(f"Avg Reward (Last 10): {np.mean(self.recent_rewards):.1f}")
        print(f"Current Noise Scale: {self.current_metrics['noise_scale']:.3f}")

    def _format_time(self, seconds):
        """将秒转换为可读时间格式"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds // 60:.0f}m {seconds % 60:.0f}s"
        else:
            return f"{seconds // 3600:.0f}h {(seconds % 3600) // 60:.0f}m"

    def close(self):
        """关闭进度条"""
        self.progress_bar.close()
        total_time = time.time() - self.start_time
        print(f"\nTraining completed in {self._format_time(total_time)}")