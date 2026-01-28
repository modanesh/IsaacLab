# Copyright (c) 2022-2025, The Isaac Lab Project Developers
# SPDX-License-Identifier: BSD-3-Clause

from isaaclab.assets import RigidObjectCfg
from isaaclab.sensors import FrameTransformerCfg
from isaaclab.sensors.frame_transformer.frame_transformer_cfg import OffsetCfg
from isaaclab.sim.schemas.schemas_cfg import RigidBodyPropertiesCfg
from isaaclab.sim.spawners.from_files.from_files_cfg import UsdFileCfg
from isaaclab.utils import configclass
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR
from isaaclab_tasks.manager_based.manipulation.lift import mdp
from isaaclab_tasks.manager_based.manipulation.lift.lift_env_cfg import LiftEnvCfg

# Import the updated robot config
from isaaclab_assets.robots.flexiv import FLEXIV_WITH_GRIPPER_CFG
from isaaclab.markers.config import FRAME_MARKER_CFG


@configclass
class FlexivCubeLiftEnvCfg(LiftEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # 1. Robot
        self.scene.robot = FLEXIV_WITH_GRIPPER_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")

        # 2. Arm Action
        self.actions.arm_action = mdp.JointPositionActionCfg(
            asset_name="robot",
            joint_names=["joint[1-7]"],
            scale=0.35,
            use_default_offset=True
        )

        # 3. Gripper Action
        # The inspection confirmed 'finger_joint' is REVOLUTE with limit ~0.78 rads.
        # DO NOT use 0.8 meters here.
        self.actions.gripper_action = mdp.BinaryJointPositionActionCfg(
            asset_name="robot",
            joint_names=["finger_joint"],
            # Open = 0.05 rads
            open_command_expr={"finger_joint": 0.05},
            # Close = 0.7 rads (Safely inside the 0.78 limit)
            close_command_expr={"finger_joint": 0.7},
        )

        # 4. End Effector / Command Body
        self.commands.object_pose.body_name = "flange"

        # 5. Object
        self.scene.object = RigidObjectCfg(
            prim_path="{ENV_REGEX_NS}/Object",
            init_state=RigidObjectCfg.InitialStateCfg(pos=[0.5, 0, 0.055], rot=[1, 0, 0, 0]),
            spawn=UsdFileCfg(
                usd_path=f"{ISAAC_NUCLEUS_DIR}/Props/Blocks/DexCube/dex_cube_instanceable.usd",
                scale=(0.8, 0.8, 0.8),
                rigid_props=RigidBodyPropertiesCfg(
                    solver_position_iteration_count=16,
                    solver_velocity_iteration_count=1,
                    max_angular_velocity=1000.0,
                    max_linear_velocity=1000.0,
                    max_depenetration_velocity=5.0,
                    disable_gravity=False,
                ),
            ),
        )

        # 6. EE Frame (Visualizer & Reward Calculation)
        marker_cfg = FRAME_MARKER_CFG.copy()
        marker_cfg.markers["frame"].scale = (0.1, 0.1, 0.1)
        marker_cfg.prim_path = "/Visuals/FrameTransformer"

        self.scene.ee_frame = FrameTransformerCfg(
            prim_path="{ENV_REGEX_NS}/Robot/base_link",
            debug_vis=False,
            visualizer_cfg=marker_cfg,
            target_frames=[
                FrameTransformerCfg.FrameCfg(
                    prim_path="{ENV_REGEX_NS}/Robot/flange",
                    name="end_effector",
                    # Z-offset 0.15m places the frame roughly between the gripper fingers
                    offset=OffsetCfg(
                        pos=[0.0, 0.0, 0.15],
                    ),
                ),
            ],
        )


@configclass
class FlexivCubeLiftEnvCfgPlay(FlexivCubeLiftEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        self.observations.policy.enable_corruption = False