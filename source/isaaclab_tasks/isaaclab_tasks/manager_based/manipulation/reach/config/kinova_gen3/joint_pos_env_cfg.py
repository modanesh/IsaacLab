# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import math

from isaaclab.utils import configclass
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg

import isaaclab_tasks.manager_based.manipulation.reach.mdp as mdp
from isaaclab_tasks.manager_based.manipulation.reach.reach_env_cfg import ReachEnvCfg

##
# Pre-defined configs
##
from isaaclab_assets import KINOVA_GEN3_N7_CFG  # isort: skip


##
# Environment configuration
##


@configclass
class KinovaGen3ReachEnvCfg(ReachEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()

        # switch robot to Kinova Gen3
        self.scene.robot = KINOVA_GEN3_N7_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")

        # ==========================================
        # TODO: TASK 1 - BASELINE SETUP
        # ==========================================
        # 1. Add the missing reward terms for end-effector tracking here.
        #    You will need to define them and assign them to self.rewards
        #    (e.g., self.rewards.my_tracking_reward = RewTerm(...))

        # ==========================================

        # override actions
        self.actions.arm_action = mdp.JointPositionActionCfg(
            asset_name="robot", joint_names=["joint_[1-7]"], scale=0.5, use_default_offset=True
        )

        # override command generator body
        # end-effector is along z-direction
        # TODO: TASK 1 - Identify and set the correct end-effector body name
        self.commands.ee_pose.body_name = "TODO_FIND_END_EFFECTOR_NAME"
        self.commands.ee_pose.ranges.pitch = (math.pi, math.pi)


@configclass
class KinovaGen3ReachEnvCfg_PLAY(KinovaGen3ReachEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()
        # make a smaller scene for play
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        # disable randomization for play
        self.observations.policy.enable_corruption = False