#from env import  stkenv
#from DDPG import  DDPGAgent
#env = stkenv(100)
#action_dim = env.observation_space.shape[0]
#state_dim = 38
#agent = DDPGAgent(state_dim, action_dim, 0.5)
#记得修改一下机动的参考坐标用J2000，以及选中mass更新
# 要把智能体决策 和 追逐着决策融合在一块！

#需要在训练中 体现训练进度(进度条) 需要有可视化图表
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # 必须放在所有import之前
from comtypes.gen import (STKObjects,
                          STKUtil, AgStkGatorLib)  # 从生成的库中获取STK的相关函数
from comtypes.client import (CreateObject,
                             GetActiveObject, GetEvents, CoGetObject, ShowEvents) # 导入生成和获取物体的库
import os
import time
import torch
from args import get_args
from DDPG import DDPGAgent
from utils.Logger import DDPGLogger
from utils.progress import TrainingProgress
from utils.visualizer import TrainingVisualizer
from env import stkenv
from chase_update_finite import update_chase
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np
from del_files import delete_subfolders
def main():
    # 解析参数
    args = get_args()

    # 初始化组件
    #env = STKChaseEnv(max_steps=args.max_steps)  # 使用你自己的环境
    env = stkenv(600) #在这捕捉到scenario
    root = env.root
    sc1 = env.sc1
    sc2 = env.sc2
    Animation = sc2.Animation
    Animation.AnimStepValue = 300
    animation = root.QueryInterface(STKObjects.IAgAnimation)
    agent = DDPGAgent(args)
    #记录训练过程中的数据
    episode_rewards = []
    critic_losses = []
    actor_losses = []
    q_values = []
    progress_bar = tqdm(range(args.total_episodes), desc="Training", unit="episode")
    for episode in progress_bar:
        delete_subfolders(r"D:\Datas_cxy")
        state = env.reset()
        episode_reward = 0
        done = False
        steps = 1
        k = 0
        while 1:
            if done:
                print('一论训练结束')
                print(info)
                break
            if not done :
                if k <= 2:
                    if animation.CurrentTime >= k * 14400:
                        chase = update_chase(k)  # 环境的更新
                        k += 1
                        animation.PlayForward()
                        t = chase.update()
                        t1 = []
                        for satellitename in ['Sat_44714', 'Sat_44715', 'Sat_44716', 'Sat_44717', 'Sat_44718']:
                            t1.append(t[satellitename])
                animation.PlayForward()
                if animation.CurrentTime >= steps * 600:
                    animation.Pause()
                    animation.CurrentTime = steps * 600
                    valid = 0 #先设置无效
                    while not valid: #如果是无效的就要一直选择动作 然后获取
                          action = agent.select_action(state)
                          env = stkenv(600)  # 重新获取一下句柄
                          next_state, reward, done, info, valid = env.step(action, steps, t1[0], t1[1], t1[2], t1[3], t1[4])
                    #print(reward)
                    agent.replay_buffer.push((state, next_state, action, reward, done))
                    animation.PlayForward()
                    state = next_state
                    episode_reward += reward
                    steps += 1
                    metrics = agent.update_networks()
                    if metrics:
                        print('网络更新')
                        critic_losses.append(metrics['critic_loss'])
                        actor_losses.append(metrics['actor_loss'])
                        q_values.append(metrics['q_value'])

        episode_rewards.append(episode_reward)
        if episode % args.plot_interval == 0:
            plot_metrics(episode_rewards, critic_losses, actor_losses, q_values)
            agent.save_models(save_dir=f"checkpoints/episode_{episode}")
        #print(episode_reward,np.mean(q_values[-10:]),agent.noise_scheduler.get_scale())
        progress_bar.set_postfix({
            "Reward": f"{episode_reward:.2f}",
            "Avg Q": f"{np.mean(q_values[-10:]):.2f}",
            "Noise": f"{agent.noise_scheduler.get_scale():.4f}"
        })

        # 训练结束后保存最终图表
    plot_metrics(episode_rewards, critic_losses, actor_losses, q_values, save_path="training_plot.png")

def plot_metrics(rewards, critic_loss, actor_loss, q_values, save_path=None):
    plt.figure(figsize=(12, 8))

        # 奖励曲线
    plt.subplot(2, 2, 1)
    plt.plot(rewards)
    plt.title("Episode Rewards")
    plt.xlabel("Episode")

        # Critic Loss
    plt.subplot(2, 2, 2)
    plt.plot(critic_loss)
    plt.title("Critic Loss")
    plt.xlabel("Update Step")

        # Actor Loss
    plt.subplot(2, 2, 3)
    plt.plot(actor_loss)
    plt.title("Actor Loss")
    plt.xlabel("Update Step")

        # Q Values
    plt.subplot(2, 2, 4)
    plt.plot(q_values)
    plt.title("Q Values")
    plt.xlabel("Update Step")

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()
            # 这里要写 获取到每个卫星机动的时间！ 然后下面写智能体的更新


if __name__ == "__main__":
    main()




