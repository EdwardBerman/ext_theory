import copy
import os
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import os
import ternary

def getRewardsSingle(rewards, window=1000):
    moving_avg = []
    i = window
    while i-window < len(rewards):
        moving_avg.append(np.average(rewards[i-window:i]))
        i += window

    moving_avg = np.array(moving_avg)
    return moving_avg

def plotLearningCurveAvg(rewards, window=1000, label='reward', color='b', shadow=True, ax=plt, legend=True, linestyle='-'):
    min_len = np.min(list(map(lambda x: len(x), rewards)))
    rewards = list(map(lambda x: x[:min_len], rewards))
    avg_rewards = np.mean(rewards, axis=0)
    # avg_rewards = np.concatenate(([0], avg_rewards))
    # std_rewards = np.std(rewards, axis=0)
    std_rewards = stats.sem(rewards, axis=0)
    # std_rewards = np.concatenate(([0], std_rewards))
    xs = np.arange(window, window * (avg_rewards.shape[0]+1), window)
    if shadow:
        ax.fill_between(xs, avg_rewards-std_rewards, avg_rewards+std_rewards, alpha=0.2, color=color)
    l = ax.plot(xs, avg_rewards, label=label, color=color, linestyle=linestyle, alpha=0.7)
    if legend:
        ax.legend(loc=4)
    return l

def plotEvalCurveAvg(rewards, freq=1000, label='reward', color='b', shadow=True, ax=plt, legend=True, linestyle='-'):
    min_len = np.min(list(map(lambda x: len(x), rewards)))
    rewards = list(map(lambda x: x[:min_len], rewards))
    avg_rewards = np.mean(rewards, axis=0)
    # avg_rewards = np.concatenate(([0], avg_rewards))
    # std_rewards = np.std(rewards, axis=0)
    std_rewards = stats.sem(rewards, axis=0)
    # std_rewards = np.concatenate(([0], std_rewards))
    xs = np.arange(freq, freq * (avg_rewards.shape[0]+1), freq)
    if shadow:
        ax.fill_between(xs, avg_rewards-std_rewards, avg_rewards+std_rewards, alpha=0.2, color=color)
    l = ax.plot(xs, avg_rewards, label=label, color=color, linestyle=linestyle, alpha=0.7)
    if legend:
        ax.legend(loc=4)
    return l

def plotEvalCurve(base, step=50000, use_default_cm=False, freq=1000):
    plt.style.use('ggplot')
    plt.figure(dpi=300)
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 14

    plt.rc('axes', titlesize=BIGGER_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=BIGGER_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels

    colors = "bgrycmkwbgrycmkw"
    if use_default_cm:
        color_map = {}
    else:
        color_map = {
            'equi+bufferaug': 'b',
            'equi': 'b',
            'cnn+bufferaug': 'g',
            'cnn': 'g',
            'cnn+rad': 'r',
            'cnn+drq': 'purple',
            'cnn+curl': 'orange',
            'curl': 'orange',

            'equi_both': 'b',
            'equi_actor': 'r',
            'equi_critic': 'purple',
            'cnn_both': 'g',

            'equi_rotaugall': 'b',
            'cnn_rotaugall': 'g',
            'rad_rotaugall': 'r',
            'drq_rotaugall': 'purple',
            'ferm_rotaugall': 'orange',

            'sacfd_equi': 'b',
            'sacfd_cnn': 'g',
            'sacfd_rad_cn': 'r',
            'sacfd_drq_cn': 'purple',
            'sacfd_rad': 'r',
            'sacfd_drq': 'purple',
            'sacfd_ferm': 'orange',

            'sac_equi': 'b',
            'sac_cnn': 'g',
            'sac_rad_crop': 'r',
            'sac_drq_shift': 'purple',
            'sac_curl': 'orange',

            'dqn_equi': 'b',
            'dqn_cnn': 'g',
            'dqn_rad_crop': 'r',
            'dqn_drq_shift': 'purple',
            'dqn_curl': 'orange',

            'C8': 'b',
            'C4': 'g',
            'C2': 'r',
        }

    linestyle_map = {
    }
    name_map = {
        'equi+bufferaug': 'Equivariant',
        'equi': 'Equivariant',
        'cnn+bufferaug': 'CNN',
        'cnn': 'CNN',
        'cnn+rad': 'RAD',
        'cnn+drq': 'DrQ',
        'cnn+curl': 'FERM',
        'curl': 'CURL',

        'equi_both': 'Equi Actor + Equi Critic',
        'equi_actor': 'Equi Actor + CNN Critic',
        'equi_critic': 'CNN Actor + Equi Critic',
        'cnn_both': 'CNN Actor + CNN Critic',

        'equi_rotaugall': 'Equi SACAux',
        'cnn_rotaugall': 'CNN SACAux',
        'rad_rotaugall': 'RAD Crop SACAux',
        'drq_rotaugall': 'DrQ Shift SACAux',
        'ferm_rotaugall': 'FERM SACAux',

        'sacfd_equi': 'Equi SACAux',
        'sacfd_cnn': 'CNN SACAux',
        'sacfd_rad_cn': 'RAD SO(2) SACAux',
        'sacfd_drq_cn': 'DrQ SO(2) SACAux',
        'sacfd_rad': 'RAD Crop SACAux',
        'sacfd_drq': 'DrQ Shift SACAux',
        'sacfd_ferm': 'FERM SACAux',

        'sac_equi': 'Equi SAC',
        'sac_cnn': 'CNN SAC',
        'sac_rad_crop': 'RAD Crop SAC',
        'sac_drq_shift': 'DrQ Shift SAC',
        'sac_curl': 'FERM',

        'dqn_equi': 'Equi DQN',
        'dqn_cnn': 'CNN DQN',
        'dqn_rad_crop': 'RAD Crop DQN',
        'dqn_drq_shift': 'DrQ Shift DQN',
        'dqn_curl': 'CURL DQN',
    }

    sequence = {
        'equi+bufferaug': '0',
        'equi': '0',
        'cnn+bufferaug': '1',
        'cnn': '1',
        'cnn+rad': '2',
        'cnn+drq': '3',
        'cnn+curl': '4',
        'curl': '4',

        'equi_both': '0',
        'equi_actor': '1',
        'equi_critic': '2',
        'cnn_both': '3',

        'equi_rotaugall': '0',
        'cnn_rotaugall': '1',
        'rad_rotaugall': '2',
        'drq_rotaugall': '3',
        'ferm_rotaugall': '4',

        'sacfd_equi': '0',
        'sacfd_cnn': '1',
        'sacfd_rad_cn': '2',
        'sacfd_drq_cn': '3',
        'sacfd_rad': '2',
        'sacfd_drq': '3',
        'sacfd_ferm': '4',

        'sac_equi': '0',
        'sac_cnn': '1',
        'sac_rad_crop': '2',
        'sac_drq_shift': '3',
        'sac_curl': '4',

        'dqn_equi': '0',
        'dqn_cnn': '1',
        'dqn_rad_crop': '2',
        'dqn_drq_shift': '3',
        'dqn_curl': '4',

        'C8': '0',
        'C4': '1',
        'C2': '2',
    }

    i = 0
    methods = filter(lambda x: x[0] != '.', get_immediate_subdirectories(base))
    for method in sorted(methods, key=lambda x: sequence[x] if x in sequence.keys() else x):
        rs = []
        for j, run in enumerate(get_immediate_subdirectories(os.path.join(base, method))):
            try:
                r = np.load(os.path.join(base, method, run, 'info/eval_rewards.npy'))
                rs.append(r[:step//freq])
            except Exception as e:
                print(e)
                continue

        plotEvalCurveAvg(rs, freq, label=name_map[method] if method in name_map else method,
                         color=color_map[method] if method in color_map else colors[i],
                         linestyle=linestyle_map[method] if method in linestyle_map else '-')
        i += 1


    # plt.plot([0, ep], [1.450, 1.450], label='planner')
    plt.legend(loc=0, facecolor='w', fontsize='x-large')
    plt.xlabel('number of training steps')
    # if base.find('bbp') > -1:
    plt.ylabel('eval discounted reward')
    # plt.xlim((-100, step+100))
    # plt.yticks(np.arange(0., 1.05, 0.1))
    # plt.ylim(bottom=-0.05)

    plt.tight_layout()
    plt.savefig(os.path.join(base, 'eval.png'), bbox_inches='tight',pad_inches = 0)

def plotStepRewardCurve(base, step=50000, use_default_cm=False, freq=1000):
    plt.style.use('ggplot')
    plt.figure(dpi=300)
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 14

    plt.rc('axes', titlesize=BIGGER_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=BIGGER_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels

    colors = "bgrycmkwbgrycmkw"
    if use_default_cm:
        color_map = {}
    else:
        color_map = {
            'dpos=0.05, drot=0.25pi': 'b',
            'dpos=0.05, drot=0.125pi': 'g',
            'dpos=0.03, drot=0.125pi': 'r',
            'dpos=0.1, drot=0.25pi': 'purple',

            'ban0': 'g',
            'ban2': 'r',
            'ban4': 'b',
            'ban8': 'purple',
            'ban16': 'orange',

            'C4': 'g',
            'C8': 'r',
            'D4': 'b',
            'D8': 'purple',

            '0': 'r',
            '10': 'g',
            '20': 'b',
            '40': 'purple',

            'sac+ban4': 'b',
            'sac+rot rad': 'g',
            'sac+rot rad+ban4': 'r',
            'sac+ban0': 'purple',

            'sac+aux+ban0': 'g',
            'sac+aux+ban4': 'r',
        }

    linestyle_map = {
    }
    name_map = {
        'ban0': 'buffer aug 0',
        'ban2': 'buffer aug 2',
        'ban4': 'buffer aug 4',
        'ban8': 'buffer aug 8',
        'ban16': 'buffer aug 16',

        'sac+ban4': 'SAC + buffer aug',
        'sac+rot rad': 'SAC + rot RAD',
        'sac+rot rad+ban4': 'SAC + rot RAD + buffer aug',
        'sac+ban0': 'SAC',

        'sac+aux+ban4': 'SAC + aux loss + buffer aug',
        'sac+aux+ban0': 'SAC + aux loss',

        'sac': 'SAC',
        'sacfd': 'SACfD',

        'sac+crop rad': 'SAC + crop RAD'
    }

    sequence = {
        'ban0': '0',
        'ban2': '1',
        'ban4': '2',
        'ban8': '3',
        'ban16': '4',

        'sac+ban0': '0',
        'sac+ban4': '1',
        'sac+aux+ban0': '2',
        'sac+aux+ban4': '3',
    }

    i = 0
    methods = filter(lambda x: x[0] != '.', get_immediate_subdirectories(base))
    for method in sorted(methods, key=lambda x: sequence[x] if x in sequence.keys() else x):
        rs = []
        for j, run in enumerate(get_immediate_subdirectories(os.path.join(base, method))):
            try:
                step_reward = np.load(os.path.join(base, method, run, 'info/step_reward.npy'))
                r = []
                for k in range(1, step+1, freq):
                    window_rewards = step_reward[(k <= step_reward[:, 0]) * (step_reward[:, 0] < k + freq)][:, 1]
                    if window_rewards.shape[0] > 0:
                        r.append(window_rewards.mean())
                    else:
                        break
                    # r.append(step_reward[(i <= step_reward[:, 0]) * (step_reward[:, 0] < i + freq)][:, 1].mean())
                rs.append(r)
            except Exception as e:
                print(e)
                continue

        plotEvalCurveAvg(rs, freq, label=name_map[method] if method in name_map else method,
                         color=color_map[method] if method in color_map else colors[i],
                         linestyle=linestyle_map[method] if method in linestyle_map else '-')
        i += 1


    # plt.plot([0, ep], [1.450, 1.450], label='planner')
    plt.legend(loc=0, facecolor='w', fontsize='x-large')
    plt.xlabel('number of training steps')
    # if base.find('bbp') > -1:
    plt.ylabel('discounted reward')
    # plt.xlim((-100, step+100))
    # plt.yticks(np.arange(0., 1.05, 0.1))
    # plt.ylim(bottom=-0.05)

    plt.tight_layout()
    plt.savefig(os.path.join(base, 'step_reward.png'), bbox_inches='tight',pad_inches = 0)

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def plotLearningCurve(base, ep=50000, use_default_cm=False, window=1000):
    plt.style.use('ggplot')
    plt.figure(dpi=300)
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 14

    plt.rc('axes', titlesize=BIGGER_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=BIGGER_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels

    colors = "bgrycmkwbgrycmkw"
    if use_default_cm:
        color_map = {}
    else:
        color_map = {
            'equi+bufferaug': 'b',
            'cnn+bufferaug': 'g',
            'cnn+rad': 'r',
            'cnn+drq': 'purple',
            'cnn+curl': 'orange',
        }

    linestyle_map = {

    }
    name_map = {
        'equi+bufferaug': 'Equivariant',
        'cnn+bufferaug': 'CNN',
        'cnn+rad': 'RAD',
        'cnn+drq': 'DrQ',
        'cnn+curl': 'FERM',
    }

    sequence = {
        'equi+equi': '0',
        'cnn+cnn': '1',
        'cnn+cnn+aug': '2',
        'equi_fcn_asr': '3',
        'tp': '4',

        'equi_fcn': '0',
        'fcn_si': '1',
        'fcn_si_aug': '2',
        'fcn': '3',

        'equi+deictic': '2',
        'cnn+deictic': '3',

        'q1_equi+q2_equi': '0',
        'q1_equi+q2_cnn': '1',
        'q1_cnn+q2_equi': '2',
        'q1_cnn+q2_cnn': '3',

        'q1_equi+q2_deictic': '0.5',
        'q1_cnn+q2_deictic': '4',

        'equi_fcn_': '1',

        '5l_equi_equi': '0',
        '5l_equi_deictic': '1',
        '5l_equi_cnn': '2',
        '5l_cnn_equi': '3',
        '5l_cnn_deictic': '4',
        '5l_cnn_cnn': '5',

    }

    # house1-4
    # plt.plot([0, 100000], [0.974, 0.974], label='expert', color='pink')
    # plt.axvline(x=10000, color='black', linestyle='--')

    # house1-5
    # plt.plot([0, 50000], [0.974, 0.974], label='expert', color='pink')
    # 0.004 pos noise
    # plt.plot([0, 50000], [0.859, 0.859], label='expert', color='pink')

    # house1-6 0.941

    # house2
    # plt.plot([0, 50000], [0.979, 0.979], label='expert', color='pink')
    # plt.axvline(x=20000, color='black', linestyle='--')

    # house3
    # plt.plot([0, 50000], [0.983, 0.983], label='expert', color='pink')
    # plt.plot([0, 50000], [0.911, 0.911], label='expert', color='pink')
    # 0.996
    # 0.911 - 0.01

    # house4
    # plt.plot([0, 50000], [0.948, 0.948], label='expert', color='pink')
    # plt.plot([0, 50000], [0.862, 0.862], label='expert', color='pink')
    # 0.875 - 0.006
    # 0.862 - 0.007 *
    # stack
    # plt.plot([0, 100000], [0.989, 0.989], label='expert', color='pink')
    # plt.axvline(x=10000, color='black', linestyle='--')

    i = 0
    methods = filter(lambda x: x[0] != '.', get_immediate_subdirectories(base))
    for method in sorted(methods, key=lambda x: sequence[x] if x in sequence.keys() else x):
        rs = []
        for j, run in enumerate(get_immediate_subdirectories(os.path.join(base, method))):
            try:
                r = np.load(os.path.join(base, method, run, 'info/rewards.npy'))
                if method.find('BC') >= 0 or method.find('tp') >= 0:
                    rs.append(r[-window:].mean())
                else:
                    rs.append(getRewardsSingle(r[:ep], window=window))
            except Exception as e:
                print(e)
                continue

        if method.find('BC') >= 0 or method.find('tp') >= 0:
            avg_rewards = np.mean(rs, axis=0)
            std_rewards = stats.sem(rs, axis=0)

            plt.plot([0, ep], [avg_rewards, avg_rewards],
                     label=name_map[method] if method in name_map else method,
                     color=color_map[method] if method in color_map else colors[i])
            plt.fill_between([0, ep], avg_rewards - std_rewards, avg_rewards + std_rewards, alpha=0.2, color=color_map[method] if method in color_map else colors[i])
        else:
            plotLearningCurveAvg(rs, window, label=name_map[method] if method in name_map else method,
                                 color=color_map[method] if method in color_map else colors[i],
                                 linestyle=linestyle_map[method] if method in linestyle_map else '-')
        i += 1


    # plt.plot([0, ep], [1.450, 1.450], label='planner')
    plt.legend(loc=0, facecolor='w', fontsize='x-large')
    plt.xlabel('number of episodes')
    # if base.find('bbp') > -1:
    plt.ylabel('discounted reward')

    # plt.xlim((-100, ep+100))
    # plt.yticks(np.arange(0., 1.05, 0.1))

    plt.tight_layout()
    plt.savefig(os.path.join(base, 'plot.png'), bbox_inches='tight',pad_inches = 0)

def plotSuccessRate(base, ep=50000, use_default_cm=False, window=1000):
    plt.style.use('ggplot')
    plt.figure(dpi=300)
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 14

    plt.rc('axes', titlesize=BIGGER_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=BIGGER_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels

    colors = "bgrycmkwbgrycmkw"
    if use_default_cm:
        color_map = {}
    else:
        color_map = {
            'equi+bufferaug': 'b',
            'cnn+bufferaug': 'g',
            'cnn+rad': 'r',
            'cnn+drq': 'purple',
            'cnn+curl': 'orange',
        }

    linestyle_map = {
    }
    name_map = {
    }

    sequence = {
    }

    i = 0
    methods = filter(lambda x: x[0] != '.', get_immediate_subdirectories(base))
    for method in sorted(methods, key=lambda x: sequence[x] if x in sequence.keys() else x):
        rs = []
        for j, run in enumerate(get_immediate_subdirectories(os.path.join(base, method))):
            try:
                r = np.load(os.path.join(base, method, run, 'info/success_rate.npy'))
                if method.find('BC') >= 0 or method.find('tp') >= 0:
                    rs.append(r[-window:].mean())
                else:
                    rs.append(getRewardsSingle(r[:ep], window=window))
            except Exception as e:
                print(e)
                continue

        if method.find('BC') >= 0 or method.find('tp') >= 0:
            avg_rewards = np.mean(rs, axis=0)
            std_rewards = stats.sem(rs, axis=0)

            plt.plot([0, ep], [avg_rewards, avg_rewards],
                     label=name_map[method] if method in name_map else method,
                     color=color_map[method] if method in color_map else colors[i])
            plt.fill_between([0, ep], avg_rewards - std_rewards, avg_rewards + std_rewards, alpha=0.2, color=color_map[method] if method in color_map else colors[i])
        else:
            plotLearningCurveAvg(rs, window, label=name_map[method] if method in name_map else method,
                                 color=color_map[method] if method in color_map else colors[i],
                                 linestyle=linestyle_map[method] if method in linestyle_map else '-')
        i += 1


    # plt.plot([0, ep], [1.450, 1.450], label='planner')
    plt.legend(loc=0, facecolor='w', fontsize='x-large')
    plt.xlabel('number of episodes')
    # if base.find('bbp') > -1:
    plt.ylabel('success rate')

    # plt.xlim((-100, ep+100))
    # plt.yticks(np.arange(0., 1.05, 0.1))

    plt.tight_layout()
    plt.savefig(os.path.join(base, 'sr.png'), bbox_inches='tight',pad_inches = 0)

def plotSuccessRateIncorrect(base, ep=50000, use_default_cm=False, plot_UB=True):
    plt.style.use('ggplot')
    plt.figure(dpi=300)
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 14

    plt.rc('axes', titlesize=BIGGER_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=BIGGER_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels

    colors = "bgrycmkwbgrycmkw"
    if use_default_cm:
        color_map = {}
    else:
        color_map = {
            "D1": 'r',
            "CNN": 'b',
            "D1_UB": 'g',
        }

    linestyle_map = {
    }
    name_map = {
        "D1": 'D1',
        "CNN": 'CNN',
        "D1_UB": 'D1 UB',
    }

    sequence = {
        "D1": 0,
        "CNN": 1,
    }

    inner_sequence = {
        "0": 0,
        "0.2": 1,
        "0.4": 2,
        "0.6": 3,
        "0.8": 4,
        "1": 5,
    }

    
    methods = filter(lambda x: x[0] != '.', get_immediate_subdirectories(base))
    for method in sorted(methods, key=lambda x: sequence[x] if x in sequence.keys() else x):
        current_path = os.path.join(base, method)
        ratios = filter(lambda x: x[0] != '.', get_immediate_subdirectories(current_path))
        i = 0
        avg_sr_list = []
        std_sr_list = []
        for ratio in sorted(ratios, key=lambda x: inner_sequence[x] if x in inner_sequence.keys() else x):
            rs = []
            for j, run in enumerate(get_immediate_subdirectories(os.path.join(current_path, ratio))):
                try:
                    r = np.load(os.path.join(current_path, ratio, run, 'info/eval_success.npy'))
                    rs.append(np.max(r))
                    
                except Exception as e:
                    print(e)
                    continue

            avg_sr = np.mean(rs)
            std_sr_list.append(stats.sem(rs))
            avg_sr_list.append(avg_sr)

        avg_sr_list = np.array(avg_sr_list)
        std_sr_list = np.array(std_sr_list)
        plt.plot([i for i in inner_sequence.keys()], avg_sr_list,
                    label=name_map[method] if method in name_map else method,
                    color=color_map[method] if method in color_map else method[i])
        
        # plotLearningCurveAvg(avg_sr_list, window, label=name_map[method] if method in name_map else method,
        #                          color=color_map[method] if method in color_map else colors[i],
        #                          linestyle=linestyle_map[method] if method in linestyle_map else '-')

        # std_rewards = np.concatenate(([0], std_rewards))
        
        # xs = np.arange(window, window * (avg_sr_list.shape[0]+1), window)
        plt.fill_between([i for i in inner_sequence.keys()], avg_sr_list-std_sr_list, avg_sr_list+std_sr_list, alpha=0.2, color=color_map[method])
    
    if plot_UB:
        method = 'D1_UB'
        avg_sr_list = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1])
        plt.plot([i for i in inner_sequence.keys()], avg_sr_list,
                    label=name_map[method] if method in name_map else method,
                    color=color_map[method] if method in color_map else method[i])


    # plt.plot([0, ep], [1.450, 1.450], label='planner')
    plt.legend(loc=0, facecolor='w', fontsize='x-large')
    plt.xlabel('correct ratio')
    # if base.find('bbp') > -1:
    plt.ylabel('test success rate')

    # plt.xlim((-0.05, 1.05))
    plt.ylim((-0.05, 1.05))
    # plt.yticks(np.arange(-0.05, 1.05))

    plt.tight_layout()
    plt.savefig(os.path.join(base, 'sr.png'), bbox_inches='tight',pad_inches = 0)

def showPerformance(base):
    methods = sorted(filter(lambda x: x[0] != '.', get_immediate_subdirectories(base)))
    for method in methods:
        rs = []
        for j, run in enumerate(get_immediate_subdirectories(os.path.join(base, method))):
            try:
                r = np.load(os.path.join(base, method, run, 'info/rewards.npy'))
                rs.append(r[-1000:].mean())
            except Exception as e:
                print(e)
        print('{}: {:.3f}'.format(method, np.mean(rs)))


def plotTDErrors():
    plt.style.use('ggplot')
    colors = "bgrycmkw"
    method_map = {
        'ADET': 'm',
        'ADET+Q*': 'g',
        'DAGGER': 'k',
        'DQN': 'c',
        'DQN+guided': 'y',
        'DQN+Q*': 'b',
        'DQN+Q*+guided': 'r',
        "DQfD": 'chocolate',
        "DQfD+Q*": 'grey'
    }
    i = 0

    base = '/media/dian/hdd/unet/perlin'
    for method in sorted(get_immediate_subdirectories(base)):
        rs = []
        if method[0] == '.' or method == 'DAGGER' or method == 'DQN':
            continue
        for j, run in enumerate(get_immediate_subdirectories(os.path.join(base, method))):
            try:
                r = np.load(os.path.join(base, method, run, 'info/td_errors.npy'))
                rs.append(getRewardsSingle(r[:120000], window=1000))
            except Exception as e:
                continue
        if method in method_map:
            plotLearningCurveAvg(rs, 1000, label=method, color=method_map[method])
        else:
            plotLearningCurveAvg(rs, 1000, label=method, color=colors[i])
        # plotLearningCurveAvg(rs, 1000, label=method, color=colors[i])
        i += 1

    plt.legend(loc=0)
    plt.xlabel('number of training steps')
    plt.ylabel('TD error')
    plt.yscale('log')
    # plt.ylim((0.8, 0.93))
    plt.show()

def plotLoss(base, step, name='model_holdout_losses'):
    colors = "bgrycmkw"
    method_map = {
        'mlp': 'MLP',
        'dssz': 'INV',
        'invz': 'INV',
    }
    i = 0

    data = {}
    for method in get_immediate_subdirectories(base):
        rs = []
        test_loss = []
        test_rank = []
        test_err = []
        test_err_norm = []
        for j, run in enumerate(get_immediate_subdirectories(os.path.join(base, method))):
            try:
                r = np.load(os.path.join(base, method, run, 'info/{}.npy'.format(name)))
                rs.append(r[:, 0])
                # test_loss.append(r.min())
                test_loss.append(r[r[:, 0].argmin(), 1])
                test_rank.append(r[r[:, 0].argmin(), 2])
                test_err.append(r[r[:, 0].argmin(), 3])
                test_err_norm.append(r[r[:, 0].argmin(), 4])
                # test_loss.append(np.sort(r)[:5].mean())
            except Exception as e:
                continue
        assert j == 9

        print('{}, ${:.3f} \pm {:.3f}$'
              .format(method,
                      np.mean(test_loss), stats.sem(test_loss),
                      ))
        # print('${:.3f} \pm {:.3f}$'
        #       .format(np.mean(test_loss), stats.sem(test_loss),
        #               ))

        model, ndata, cr, icr = method.split('_')
        if model not in data.keys():
            data[model] = {'cr': [],
                           'icr': [],
                           'both': []}
        ndata = int(ndata.removeprefix('ndata'))
        cr = float(cr.removeprefix('cr'))
        icr = float(icr.removeprefix('icr'))
        if cr == 0 and icr == 0:
            data[model]['cr'].append([cr, np.mean(test_loss), stats.sem(test_loss)])
            data[model]['icr'].append([icr, np.mean(test_loss), stats.sem(test_loss)])
        elif cr > 0 and icr == 0:
            data[model]['cr'].append([cr, np.mean(test_loss), stats.sem(test_loss)])
            if cr == 1:
                data[model]['both'].append([icr, np.mean(test_loss), stats.sem(test_loss)])
        elif cr == 0 and icr > 0:
            data[model]['icr'].append([icr, np.mean(test_loss), stats.sem(test_loss)])
            if icr == 1:
                data[model]['both'].append([icr, np.mean(test_loss), stats.sem(test_loss)])
        elif cr + icr == 1:
            data[model]['both'].append([icr, np.mean(test_loss), stats.sem(test_loss)])
        i += 1

    for r in ['cr', 'icr', 'both']:
        plt.style.use('ggplot')
        plt.figure(dpi=300)

        MEDIUM_SIZE = 12
        BIGGER_SIZE = 14

        plt.rc('axes', titlesize=BIGGER_SIZE)  # fontsize of the axes title
        plt.rc('axes', labelsize=BIGGER_SIZE)  # fontsize of the x and y labels
        plt.rc('xtick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
        plt.rc('ytick', labelsize=MEDIUM_SIZE)  # fontsize of the tick labels

        if r == 'both':
            plt.plot([0, 1], [1, 0.5], label='INV UB', c='g')

        for method in data.keys():
            d = data[method][r]
            d = np.array(d)
            d = d[d[:, 0].argsort()]
            xs = d[:, 0]
            plt.plot(xs, d[:, 1], label=method_map[method])
            plt.fill_between(xs, d[:, 1] - d[:, 2], d[:, 1] + d[:, 2], alpha=0.2)

        plt.legend(loc=0, facecolor='w', fontsize='x-large')
        if r == 'cr':
            plt.xlabel('extrinsic - correct')
        elif r == 'icr':
            plt.xlabel('extrinsic - incorrect')
        elif r == 'both':
            plt.xlabel('correct - incorrect')

        plt.ylabel('test sr')
        plt.tight_layout()
        plt.ylim(-0.05, 1.05)
        plt.savefig(os.path.join(base, '{}.png'.format(r)), bbox_inches='tight', pad_inches=0)
        plt.close()


if __name__ == '__main__':
    # base = '/media/dian/hdd/mrun_results/transfer/0822_topdown'
    # for sub in os.listdir(base):
    #     if not os.path.isdir(os.path.join(base, sub)):
    #         continue
    #     plotEvalCurve(os.path.join(base, sub), 10000, freq=500)

    base = '/home/mingxi/workspace/NIPS/outputs/figure/0515_incorrect_plot_test'
    plotSuccessRateIncorrect(base, ep=20000)