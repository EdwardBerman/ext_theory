import os
import sys
import time
import copy
import collections
from tqdm import tqdm

sys.path.append('./')
sys.path.append('..')
from utils.parameters import *
from storage.buffer import QLearningBuffer
from utils.logger import Logger
from utils.schedules import LinearSchedule
from utils.env_wrapper import EnvWrapper

from utils.create_agent import createAgent
import threading

from utils.torch_utils import ExpertTransition
import matplotlib.pyplot as plt



def set_seed(s):
    np.random.seed(s)
    torch.manual_seed(s)
    torch.cuda.manual_seed(s)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False



def train_step(agent, replay_buffer, logger, p_beta_schedule):
    if buffer_type[:3] == 'per':
        beta = p_beta_schedule.value(logger.num_training_steps)
        batch, weights, batch_idxes = replay_buffer.sample(batch_size, beta)
        loss, td_error = agent.update(batch)
        new_priorities = np.abs(td_error.cpu()) + np.stack([t.expert for t in batch]) * per_expert_eps + per_eps
        replay_buffer.update_priorities(batch_idxes, new_priorities)
        logger.expertSampleBookkeeping(
            np.stack(list(zip(*batch))[-1]).sum() / batch_size)
    else:
        batch = replay_buffer.sample(batch_size)
        loss, td_error = agent.update(batch)

    logger.trainingBookkeeping(loss, td_error.mean().item())
    logger.num_training_steps += 1
    if logger.num_training_steps % target_update_freq == 0:
        agent.updateTarget()

def preTrainCURLStep(agent, replay_buffer, logger):
    if buffer_type[:3] == 'per':
        batch, weights, batch_idxes = replay_buffer.sample(batch_size, per_beta)
    else:
        batch = replay_buffer.sample(batch_size)
    loss = agent.updateCURLOnly(batch)
    logger.trainingBookkeeping(loss, 0)

def saveModelAndInfo(logger, agent):
    if save_multi_freq > 0:
        if logger.num_training_steps % save_multi_freq == 0:
            logger.saveMultiModel(logger.num_training_steps, env, agent)
    logger.saveModel(logger.num_steps, env, agent)
    logger.saveLearningCurve(20)
    logger.saveLossCurve(100)
    # logger.saveTdErrorCurve(100)
    logger.saveStepLeftCurve(100)
    logger.saveExpertSampleCurve(100)
    logger.saveEvalCurve()
    logger.saveRewards()
    logger.saveLosses()
    logger.saveTdErrors()
    logger.saveEvalRewards()

def evaluate(envs, agent, logger):
    states, obs = envs.reset()
    evaled = 0
    temp_reward = [[] for _ in range(num_eval_processes)]
    eval_rewards = []
    eval_success = []
    if not no_bar:
        eval_bar = tqdm(total=num_eval_episodes, position=1, leave=False)
    while evaled < num_eval_episodes:
        actions_star_idx, actions_star = agent.getGreedyActions(states, obs)
        states_, obs_, rewards, dones = envs.step(actions_star, auto_reset=True)
        rewards = rewards.numpy()
        dones = dones.numpy()
        states = copy.copy(states_)
        obs = copy.copy(obs_)
        for i, r in enumerate(rewards.reshape(-1)):
            temp_reward[i].append(r)
        evaled += int(np.sum(dones))
        for i, d in enumerate(dones.astype(bool)):
            if d:
                R = 0
                for r in reversed(temp_reward[i]):
                    R = r + gamma * R
                eval_rewards.append(R)
                eval_success.append(np.sum(temp_reward[i]))
                temp_reward[i] = []
        if not no_bar:
            eval_bar.update(evaled - eval_bar.n)
    logger.eval_rewards.append(np.mean(eval_rewards[:num_eval_episodes]))
    logger.eval_success.append(np.mean(eval_success[:num_eval_episodes]))
    if not no_bar:
        eval_bar.clear()
        eval_bar.close()

def evaluateMix(envs, agent, logger):
    # TODO: refactor this function to calculate eval episode based on num_eval_episodes
    envs.setFlag([True for i in range(num_processes)])
    states, obs = envs.reset()
    evaled_stack = 0
    evaled_sort = 0
    temp_reward_stack = [[] for _ in range(num_eval_processes)]
    eval_rewards = []
    eval_success = []
    temp_reward_sort = [[] for _ in range(num_eval_processes)]
    if not no_bar:
        eval_bar1 = tqdm(total=planner_mix_stack//4, position=1, leave=False)
    while evaled_stack < planner_mix_stack//4:
        actions_star_idx, actions_star = agent.getGreedyActions(states, obs)
        states_, obs_, rewards, dones = envs.step(actions_star, auto_reset=True)
        rewards = rewards.numpy()
        dones = dones.numpy()
        states = copy.copy(states_)
        obs = copy.copy(obs_)
        for i, r in enumerate(rewards.reshape(-1)):
            temp_reward_stack[i].append(r)
        evaled_stack += int(np.sum(dones))
        for i, d in enumerate(dones.astype(bool)):
            if d:
                R = 0
                for r in reversed(temp_reward_stack[i]):
                    R = r + gamma * R
                if len(eval_rewards) < planner_mix_stack//4:
                    eval_rewards.append(R)
                    eval_success.append(np.sum(temp_reward_stack[i]))
                    temp_reward_stack[i] = []
        if not no_bar:
            eval_bar1.set_description('Task Stack')
            eval_bar1.update(evaled_stack - eval_bar1.n)
    if not no_bar:
        eval_bar1.clear()
        eval_bar1.close()

    envs.setFlag([False for i in range(num_processes)])
    states, obs = envs.reset()
    if not no_bar:
        eval_bar2 = tqdm(total=planner_mix_sort//4, position=1, leave=False)
    while evaled_sort < planner_mix_sort//4:
        actions_star_idx, actions_star = agent.getGreedyActions(states, obs)
        states_, obs_, rewards, dones = envs.step(actions_star, auto_reset=True)
        rewards = rewards.numpy()
        dones = dones.numpy()
        states = copy.copy(states_)
        obs = copy.copy(obs_)
        for i, r in enumerate(rewards.reshape(-1)):
            temp_reward_sort[i].append(r)
        evaled_sort += int(np.sum(dones))
        for i, d in enumerate(dones.astype(bool)):
            if d:
                R = 0
                for r in reversed(temp_reward_sort[i]):
                    R = r + gamma * R
                if len(eval_rewards) < planner_mix_stack//4 + planner_mix_sort//4:
                    eval_rewards.append(R)
                    eval_success.append(np.sum(temp_reward_sort[i]))
                    temp_reward_sort[i] = []
        if not no_bar:
            eval_bar2.set_description('Task Sort')
            eval_bar2.update(evaled_sort - eval_bar2.n)
    if not no_bar:
        eval_bar2.clear()
        eval_bar2.close()

    logger.eval_rewards.append(np.mean(eval_rewards))
    logger.eval_success.append(np.mean(eval_success))

def countParameters(m):
    return sum(p.numel() for p in m.parameters() if p.requires_grad)

def train():
    eval_thread = None
    start_time = time.time()
    if seed is not None:
        set_seed(seed)
    # setup env
    print('creating envs')
    envs = EnvWrapper(num_processes, simulator, env, env_config, planner_config)
    if simulate_n > 0 and not load_buffer:
        planner_envs = EnvWrapper(1, simulator, env, env_config, planner_config)
    # setup agent
    agent = createAgent()
    eval_agent = createAgent(test=True)
    # .train() is required for equivariant network
    agent.train()
    eval_agent.train()
    if load_model_pre:
        agent.loadModel(load_model_pre)

    # logging
    simulator_str = copy.copy(simulator)
    if simulator == 'pybullet':
        simulator_str += ('_' + robot)
    log_dir = os.path.join(log_pre, '{}_{}'.format(alg, model))
    if note:
        log_dir += '_'
        log_dir += note

    logger = Logger(log_dir, env, 'train', num_processes, max_train_step, gamma, log_sub)
    hyper_parameters['model_shape'] = agent.getModelStr()
    logger.saveParameters(hyper_parameters)


    if buffer_type == 'normal':
        replay_buffer = QLearningBuffer(buffer_size)
    else:
        raise NotImplementedError
    exploration = LinearSchedule(schedule_timesteps=explore, initial_p=init_eps, final_p=final_eps)
    p_beta_schedule = LinearSchedule(schedule_timesteps=max_train_step, initial_p=per_beta, final_p=1.0)

    if env != 'close_loop_block_arranging':
        if planner_episode > 0 and not load_sub:
            planner_envs = envs
            planner_num_process = num_processes
            j = 0
            states, obs = planner_envs.reset()
            s = 0
            if not no_bar:
                planner_bar = tqdm(total=planner_episode, leave=True)
            local_transitions = [[] for _ in range(planner_num_process)]

            while j < planner_episode:
                plan_actions = planner_envs.getNextAction()
                planner_actions_star_idx, planner_actions_star = agent.getActionFromPlan(plan_actions)
                states_, obs_, rewards, dones = planner_envs.step(planner_actions_star, auto_reset=True)
                for i in range(planner_num_process):
                    transition = ExpertTransition(states[i].numpy(), obs[i].numpy().astype(np.float32), planner_actions_star_idx[i].numpy(),
                                                rewards[i].numpy(), states_[i].numpy(), obs_[i].numpy(), dones[i].numpy(),
                                                np.array(100), np.array(1))
                    local_transitions[i].append(transition)
                    


                states = copy.copy(states_)
                obs = copy.copy(obs_)

                for i in range(planner_num_process):
                    if dones[i] and rewards[i]:
                        for t in local_transitions[i]:
                            replay_buffer.add(t)
                        
                        local_transitions[i] = []
                        j += 1
                        s += 1
                        if not no_bar:
                            planner_bar.set_description('{:.3f}/{}, AVG: {:.3f}'.format(s, j, float(s) / j if j != 0 else 0))
                            planner_bar.update(1)
                        if j == planner_episode:
                            break
                    elif dones[i]:
                        local_transitions[i] = []
            if not no_bar:
                planner_bar.close()

    else:
        assert planner_mix_stack>0 or planner_mix_sort>0
        if (planner_mix_stack+planner_mix_sort) > 0 and not load_sub:
            planner_envs = envs
            planner_num_process = num_processes
            count_stack = 0
            count_sort = 0

            planner_envs.setFlag([True for i in range(num_processes)])
            states, obs = planner_envs.reset()
            s_stack = 0
            if not no_bar:
                planner_bar1 = tqdm(total=planner_mix_stack, leave=True)
            local_transitions = [[] for _ in range(planner_num_process)]
            while count_stack < planner_mix_stack:
                plan_actions = planner_envs.getNextAction()
                planner_actions_star_idx, planner_actions_star = agent.getActionFromPlan(plan_actions)
                states_, obs_, rewards, dones = planner_envs.step(planner_actions_star, auto_reset=True)
                for i in range(planner_num_process):
                    transition = ExpertTransition(states[i].numpy(), obs[i].numpy().astype(np.float32), planner_actions_star_idx[i].numpy(),
                                                rewards[i].numpy(), states_[i].numpy(), obs_[i].numpy(), dones[i].numpy(),
                                                np.array(100), np.array(1))
                    local_transitions[i].append(transition)
                    
                states = copy.copy(states_)
                obs = copy.copy(obs_)
                for i in range(planner_num_process):
                    if dones[i] and rewards[i]:
                        for t in local_transitions[i]:
                            replay_buffer.add(t)
                        
                        local_transitions[i] = []
                        count_stack += 1
                        s_stack += 1
                        if not no_bar:
                            planner_bar1.set_description('Planner Stack: {:.3f}/{}, AVG: {:.3f}'.format(s_stack, count_stack,
                                                                                        float(s_stack) / count_stack if count_stack != 0 else 0))
                            planner_bar1.update(1)
                        if count_stack == planner_episode:
                            break
                    elif dones[i]:
                        local_transitions[i] = []
            if not no_bar:
                planner_bar1.close()

        planner_envs.setFlag([False for i in range(num_processes)])
        states, obs = planner_envs.reset()
        s_sort = 0
        if not no_bar:
            planner_bar2 = tqdm(total=planner_mix_sort, leave=True)
        while count_sort < planner_mix_sort:
            plan_actions = planner_envs.getNextAction()
            planner_actions_star_idx, planner_actions_star = agent.getActionFromPlan(plan_actions)
            states_, obs_, rewards, dones = planner_envs.step(planner_actions_star, auto_reset=True)
            for i in range(planner_num_process):
                transition = ExpertTransition(states[i].numpy(), obs[i].numpy().astype(np.float32),
                                              planner_actions_star_idx[i].numpy(),
                                              rewards[i].numpy(), states_[i].numpy(), obs_[i].numpy(), dones[i].numpy(),
                                              np.array(100), np.array(1))

                
                local_transitions[i].append(transition)

            states = copy.copy(states_)
            obs = copy.copy(obs_)

            for i in range(planner_num_process):
                if dones[i] and rewards[i]:
                    for t in local_transitions[i]:
                        replay_buffer.add(t)
                    
                    local_transitions[i] = []
                    count_sort += 1
                    s_sort += 1
                    if not no_bar:
                        planner_bar2.set_description('Planner Sort: {:.3f}/{}, AVG: {:.3f}'.format(s_sort, count_sort,
                                                                                                   float(s_sort) / count_sort if count_sort != 0 else 0))
                        planner_bar2.update(1)
                    if count_sort == planner_episode:
                        break
                elif dones[i]:
                    local_transitions[i] = []
            
        if not no_bar:
            planner_bar2.close()

    if not no_bar:
        pbar = tqdm(total=max_train_step, position=0, leave=True)
        pbar.set_description('Episodes:0; Reward:0.0; Explore:0.0; Loss:0.0; Time:0.0')
    timer_start = time.time()

    while logger.num_training_steps < max_train_step:
        train_step(agent, replay_buffer, logger, p_beta_schedule)

        if (time.time() - start_time)/3600 > time_limit:
            break

        if not no_bar:
            timer_final = time.time()
            description = 'Eval Reward:{:.03f}; Loss:{:.03f}; Time:{:.03f}'.format(
                logger.eval_success[-1] if len(logger.eval_success) > 0 else 0, float(logger.getCurrentLoss()),
                timer_final - timer_start)
            pbar.set_description(description)
            timer_start = timer_final
            pbar.update(logger.num_training_steps-pbar.n)

        if logger.num_training_steps > 0 and eval_freq > 0 and logger.num_training_steps % eval_freq == 0:
            if eval_thread is not None:
                eval_thread.join()
            eval_agent.copyNetworksFrom(agent)
            if env != 'close_loop_block_arranging':
                eval_thread = threading.Thread(target=evaluate, args=(envs, eval_agent, logger))
            else:
                eval_thread = threading.Thread(target=evaluateMix, args=(envs, eval_agent, logger))
            eval_thread.start()

        if logger.num_training_steps % save_freq == 0:
            saveModelAndInfo(logger, agent)
        if save_multi_freq > 0:
            saveModelAndInfo(logger, agent)

    if eval_thread is not None:
        eval_thread.join()
    saveModelAndInfo(logger, agent)
    logger.saveCheckPoint(args, envs, agent, replay_buffer)
    if logger.num_training_steps >= max_train_step:
        logger.saveResult()
    envs.close()
    print('training finished')
    if not no_bar:
        pbar.close()

if __name__ == '__main__':
    train()