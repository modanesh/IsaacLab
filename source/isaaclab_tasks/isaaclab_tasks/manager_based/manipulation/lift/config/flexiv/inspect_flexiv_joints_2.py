"""
FINAL Verification - Test with soft limits disabled
"""

from isaaclab.app import AppLauncher
app_launcher = AppLauncher(headless=False)
simulation_app = app_launcher.app

import torch
import isaaclab.sim as sim_utils
from isaaclab.sim import SimulationContext, SimulationCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.assets import AssetBaseCfg, ArticulationCfg
from isaaclab.sim.spawners.from_files import GroundPlaneCfg
from isaaclab.utils import configclass
from isaaclab.actuators import ImplicitActuatorCfg

USD_PATH = "/home/mohamad/Research/IsaacLab/source/isaaclab_assets/isaaclab_assets/robots/data/flexiv/Rizon4s_with_Grav_FIXED.usd"

FLEXIV_FINAL = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=USD_PATH,
        activate_contact_sensors=False,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=5.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=8,
            solver_velocity_iteration_count=0,
        ),
        joint_drive_props=sim_utils.JointDrivePropertiesCfg(
            drive_type="none",
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        joint_pos={
            "joint1": 0.0, "joint2": -0.5, "joint3": 0.0, "joint4": 1.5,
            "joint5": 0.0, "joint6": 0.5, "joint7": 0.0, "finger_joint": 0.0,
        },
    ),
    actuators={
        "flexiv_arm": ImplicitActuatorCfg(
            joint_names_expr=["joint[1-7]"],
            effort_limit_sim=100.0, velocity_limit_sim=2.0,
            stiffness=400.0, damping=40.0,
        ),
        "gripper": ImplicitActuatorCfg(
            joint_names_expr=["finger_joint"],
            effort_limit=80.0, effort_limit_sim=80.0, velocity_limit_sim=2.0,
            stiffness=800.0, damping=30.0,
        ),
    },
    soft_joint_pos_limit_factor=0.0,  # DISABLE soft limits
)


@configclass
class TestSceneCfg(InteractiveSceneCfg):
    robot = FLEXIV_FINAL.replace(prim_path="/World/Robot")
    plane = AssetBaseCfg(prim_path="/World/GroundPlane", spawn=GroundPlaneCfg())


def main():
    print("="*80)
    print("  FINAL GRIPPER TEST (Soft Limits Disabled)")
    print("="*80)

    sim_cfg = SimulationCfg(dt=0.01)
    sim = SimulationContext(sim_cfg)
    scene_cfg = TestSceneCfg(num_envs=1, env_spacing=2.0)
    scene = InteractiveScene(scene_cfg)
    sim.reset()

    robot = scene["robot"]
    joint_names = robot.data.joint_names
    finger_idx = joint_names.index("finger_joint")

    print(f"\n✓ Robot initialized")
    print(f"✓ Soft limit factor: {robot.cfg.soft_joint_pos_limit_factor}")

    targets = torch.zeros((1, robot.num_joints), device=sim.device)
    targets[:] = robot.data.default_joint_pos

    test_targets = [
        ("OPEN", 0.0),
        ("HALF", 0.35),
        ("CLOSED", 0.7),
        ("OPEN", 0.0),
    ]

    print("\n" + "="*80)
    print("  GRIPPER MOTION TEST")
    print("="*80)

    for test_name, target_pos in test_targets:
        print(f"\n--- {test_name}: target = {target_pos:.2f} ---")

        targets[:, finger_idx] = target_pos

        for step in range(100):
            robot.set_joint_position_target(targets)
            robot.write_data_to_sim()
            sim.step()
            scene.update(dt=0.01)

            if step % 25 == 0:
                current = robot.data.joint_pos[0, finger_idx].item()
                error = abs(current - target_pos)
                print(f"  Step {step:3d}: pos = {current:6.3f} | error = {error:.4f}")

        final = robot.data.joint_pos[0, finger_idx].item()
        error = abs(final - target_pos)

        if error < 0.05:
            print(f"  ✓ SUCCESS! (error = {error:.4f})")
        else:
            print(f"  ✗ Failed (error = {error:.4f})")

    print("\n" + "="*80)
    print("  Simulation running - observe gripper")
    print("  Press Ctrl+C to exit")
    print("="*80 + "\n")

    step_count = 0
    while simulation_app.is_running():
        if step_count % 200 == 0:
            targets[:, finger_idx] = 0.7 if (step_count % 400 == 0) else 0.0
            state = "CLOSING" if targets[0, finger_idx].item() > 0.5 else "OPENING"
            print(f"[{step_count}] {state}...")

        robot.set_joint_position_target(targets)
        robot.write_data_to_sim()
        sim.step()
        scene.update(dt=0.01)
        step_count += 1

    simulation_app.close()


if __name__ == "__main__":
    main()