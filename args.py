import argparse
import torch

def get_args():
    """定义所有超参数"""
    parser = argparse.ArgumentParser(description='DDPG Training Configuration')

    # 环境参数
    parser.add_argument('--state_dim', type=int, default=38, help='状态空间维度')
    parser.add_argument('--action_dim', type=int, default=3, help='动作空间维度')
    parser.add_argument('--max_action', type=float, default=0.01, help='动作最大值')
    parser.add_argument('--max_steps', type=int, default=1000, help='单回合最大步数')

    # 训练参数
    parser.add_argument('--total_episodes', type=int, default=50, help='总训练回合数') #先设个小的
    parser.add_argument('--batch_size', type=int, default=128, help='训练批量大小')
    parser.add_argument('--gamma', type=float, default=0.99, help='折扣因子')
    parser.add_argument('--tau', type=float, default=0.005, help='软更新系数')

    # 网络参数
    parser.add_argument('--hidden_dim', type=int, default=256, help='隐藏层维度')
    parser.add_argument('--actor_lr', type=float, default=1e-4, help='Actor学习率')
    parser.add_argument('--critic_lr', type=float, default=1e-3, help='Critic学习率')
    parser.add_argument('--batchsize', type=int, default=128, help='batch值')

    # 探索参数
    parser.add_argument('--noise_initial', type=float, default=1.0, help='初始噪声比例')
    parser.add_argument('--noise_final', type=float, default=0.1, help='最终噪声比例')
    parser.add_argument('--noise_decay', type=float, default=0.995, help='噪声衰减率')
    parser.add_argument('--ou_theta', type=float, default=0.15, help='OU噪声theta参数')
    parser.add_argument('--ou_sigma', type=float, default=0.2, help='OU噪声sigma参数')
    parser.add_argument('--ou_mu', type=float, default=0.0, help='OU过程的均值参数')
    parser.add_argument('--ou_dt', type=float, default=1e-2, help='OU过程的时间步长')

    # 系统参数
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu',
                        help='计算设备')
    parser.add_argument('--log_dir', type=str, default='logs', help='日志存储目录')
    parser.add_argument('--save_interval', type=int, default=10, help='模型保存间隔')

    parser.add_argument("--plot_interval", type=int, default=5)  # 每隔多少回合绘图一次

    args, _ = parser.parse_known_args()
    return args



