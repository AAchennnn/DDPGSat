import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import threading


class TrainingVisualizer:
    def __init__(self, refresh_interval=5, history_size=200):
        """实时训练可视化工具

        Args:
            refresh_interval (int): 刷新间隔（秒）
            history_size (int): 显示的历史数据点数
        """
        # 初始化图形界面
        plt.ion()
        self.fig = plt.figure(figsize=(15, 10))
        self.axs = {
            'reward': self.fig.add_subplot(221),
            'loss': self.fig.add_subplot(222),
            'noise': self.fig.add_subplot(223),
            'q_value': self.fig.add_subplot(224)
        }

        # 数据缓存
        self.history = {
            'reward': np.zeros(history_size),
            'critic_loss': np.zeros(history_size),
            'actor_loss': np.zeros(history_size),
            'noise': np.zeros(history_size),
            'q_value': np.zeros(history_size)
        }
        self.idx = 0
        self.history_size = history_size

        # 刷新控制
        self.refresh_interval = refresh_interval
        self._running = True
        self.thread = threading.Thread(target=self._update_loop)
        self.thread.start()

    def _update_plots(self):
        """更新所有子图"""
        for ax in self.axs.values():
            ax.clear()

        # 奖励曲线
        self.axs['reward'].plot(self.history['reward'], 'b-')
        self.axs['reward'].set_title('Episode Rewards')
        self.axs['reward'].grid(True)

        # 损失曲线
        self.axs['loss'].plot(self.history['critic_loss'], 'r-', label='Critic')
        self.axs['loss'].plot(self.history['actor_loss'], 'g-', label='Actor')
        self.axs['loss'].set_title('Training Losses')
        self.axs['loss'].legend()
        self.axs['loss'].grid(True)

        # 噪声系数
        self.axs['noise'].plot(self.history['noise'], 'm-')
        self.axs['noise'].set_title('Noise Scale')
        self.axs['noise'].grid(True)

        # Q值估计
        self.axs['q_value'].plot(self.history['q_value'], 'c-')
        self.axs['q_value'].set_title('Q Value Estimation')
        self.axs['q_value'].grid(True)

        plt.tight_layout()
        plt.draw()

    def _update_loop(self):
        """后台刷新线程"""
        while self._running:
            self._update_plots()
            plt.pause(self.refresh_interval)

    def update_metrics(self, metrics):
        """更新指标数据"""
        idx = self.idx % self.history_size
        for key in self.history:
            self.history[key][idx] = metrics.get(key, 0)
        self.idx += 1

    def save_report(self, filename='training_report.pdf'):
        """生成最终训练报告"""
        with PdfPages(filename) as pdf:
            # 奖励曲线
            fig = plt.figure(figsize=(10, 6))
            plt.plot(self.history['reward'])
            plt.title('Training Rewards')
            pdf.savefig(fig)
            plt.close()

            # 损失曲线
            fig = plt.figure(figsize=(10, 6))
            plt.plot(self.history['critic_loss'], label='Critic')
            plt.plot(self.history['actor_loss'], label='Actor')
            plt.title('Training Losses')
            plt.legend()
            pdf.savefig(fig)
            plt.close()

            # 噪声衰减
            fig = plt.figure(figsize=(10, 6))
            plt.plot(self.history['noise'])
            plt.title('Noise Scale Decay')
            pdf.savefig(fig)
            plt.close()

    def close(self):
        """关闭可视化工具"""
        self._running = False
        self.thread.join()
        plt.ioff()
        plt.close()
