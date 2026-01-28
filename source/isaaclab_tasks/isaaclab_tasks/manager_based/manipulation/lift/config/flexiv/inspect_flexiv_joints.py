"""
Inspect Gripper Joint Relationships in Isaac Lab
This checks if the 5 extra gripper joints are mimic joints or need separate control
"""

from isaaclab.app import AppLauncher
app_launcher = AppLauncher(headless=True)
simulation_app = app_launcher.app

import torch
import carb
from isaaclab.sim import SimulationContext, SimulationCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.assets import AssetBaseCfg
from isaaclab.sim.spawners.from_files import GroundPlaneCfg
from isaaclab.utils import configclass
from pxr import Usd, UsdPhysics, PhysxSchema

# Import your Flexiv config
from isaaclab_assets.robots.flexiv import FLEXIV_WITH_GRIPPER_CFG


@configclass
class TestSceneCfg(InteractiveSceneCfg):
    robot = FLEXIV_WITH_GRIPPER_CFG.replace(prim_path="/World/Robot")
    plane = AssetBaseCfg(prim_path="/World/GroundPlane", spawn=GroundPlaneCfg())


def print_sep(title=""):
    print("\n" + "="*80)
    if title:
        print(f"  {title}")
        print("="*80)


def inspect_gripper_joints():
    print_sep("GRIPPER JOINT RELATIONSHIP INSPECTOR")

    # Initialize simulation
    sim_cfg = SimulationCfg(dt=0.01)
    sim = SimulationContext(sim_cfg)
    scene_cfg = TestSceneCfg(num_envs=1, env_spacing=2.0)
    scene = InteractiveScene(scene_cfg)
    sim.reset()

    robot = scene["robot"]

    # Get USD stage
    stage = simulation_app.context.get_stage()

    print("\n[1] Analyzing Gripper Joints in USD")
    print("-" * 80)

    # All gripper-related joints
    gripper_joints = [
        "finger_joint",
        "left_inner_knuckle_joint",
        "right_inner_knuckle_joint",
        "right_outer_knuckle_joint",
        "left_outer_finger_joint",
        "right_outer_finger_joint"
    ]

    # Get the robot prim path
    robot_prim = stage.GetPrimAtPath("/World/Robot")

    print(f"\nSearching for joints under: /World/Robot")

    joint_info = {}

    for prim in stage.Traverse():
        prim_path = str(prim.GetPath())
        prim_name = prim.GetName()

        if prim_name in gripper_joints and "Robot" in prim_path:
            print(f"\n  Found: {prim_name}")
            print(f"    Path: {prim_path}")

            # Check if it's a physics joint
            if prim.IsA(UsdPhysics.Joint):
                print(f"    Type: Physics Joint")

                # Check for mimic joint (PhysX specific)
                is_mimic = False
                try:
                    if prim.HasAPI(PhysxSchema.PhysxMimicJointAPI):
                        print(f"    *** MIMIC JOINT DETECTED ***")
                        is_mimic = True

                        # Get mimic properties
                        for attr in prim.GetAttributes():
                            attr_name = attr.GetName()
                            if "mimic" in attr_name.lower():
                                print(f"      {attr_name}: {attr.Get()}")
                except Exception as e:
                    # Check manually for mimic attributes
                    for attr in prim.GetAttributes():
                        attr_name = attr.GetName()
                        if "mimic" in attr_name.lower():
                            print(f"    *** MIMIC JOINT DETECTED (via attributes) ***")
                            print(f"      {attr_name}: {attr.Get()}")
                            is_mimic = True

                # Get joint limits
                lower_attr = prim.GetAttribute("physics:lowerLimit")
                upper_attr = prim.GetAttribute("physics:upperLimit")

                if lower_attr and upper_attr:
                    lower = lower_attr.Get()
                    upper = upper_attr.Get()
                    print(f"    Limits: [{lower}, {upper}]")

                # Check for drive/actuator
                has_drive = False
                for attr in prim.GetAttributes():
                    if "drive" in attr.GetName().lower():
                        has_drive = True
                        break
                print(f"    Has Drive: {has_drive}")

                # Get connected bodies
                body0_rel = prim.GetRelationship("physics:body0")
                body1_rel = prim.GetRelationship("physics:body1")

                if body0_rel and body1_rel:
                    b0 = body0_rel.GetTargets()
                    b1 = body1_rel.GetTargets()
                    if b0:
                        print(f"    Body0: {b0[0].pathString.split('/')[-1]}")
                    if b1:
                        print(f"    Body1: {b1[0].pathString.split('/')[-1]}")

                joint_info[prim_name] = {
                    "path": prim_path,
                    "has_drive": has_drive,
                    "is_mimic": is_mimic
                }

    # Analyze the results
    print_sep("ANALYSIS")

    print("\nJoint Control Summary:")
    print("-" * 80)

    mimic_joints = [name for name, info in joint_info.items() if info.get("is_mimic", False)]
    driven_joints = [name for name, info in joint_info.items() if info.get("has_drive", False)]

    print(f"\nTotal gripper joints found: {len(joint_info)}")
    print(f"Mimic joints: {len(mimic_joints)}")
    if mimic_joints:
        for name in mimic_joints:
            print(f"  - {name}")

    print(f"\nJoints with drives: {len(driven_joints)}")
    if driven_joints:
        for name in driven_joints:
            print(f"  - {name}")

    # Test actual behavior
    print_sep("BEHAVIORAL TEST")

    print("\nTesting: What happens when we move finger_joint?")
    print("-" * 80)

    joint_names = robot.data.joint_names
    finger_idx = joint_names.index("finger_joint")

    # Get indices of all gripper joints
    gripper_indices = {}
    for name in gripper_joints:
        if name in joint_names:
            gripper_indices[name] = joint_names.index(name)

    print(f"\nGripper joint indices:")
    for name, idx in gripper_indices.items():
        print(f"  {name:30s}: index {idx}")

    # Record initial positions
    initial_pos = robot.data.joint_pos[0].clone()

    print(f"\nInitial positions:")
    for name, idx in gripper_indices.items():
        print(f"  {name:30s}: {initial_pos[idx].item():7.3f}")

    # Command finger_joint to move to 0.5
    targets = torch.zeros((1, robot.num_joints), device=sim.device)
    targets[:] = robot.data.default_joint_pos
    targets[:, finger_idx] = 0.5

    print(f"\nCommanding finger_joint to 0.5...")
    print(f"Simulating for 100 steps...")

    for step in range(100):
        robot.set_joint_position_target(targets)
        robot.write_data_to_sim()
        sim.step()
        scene.update(dt=0.01)

    # Check final positions
    final_pos = robot.data.joint_pos[0]

    print(f"\nFinal positions after commanding finger_joint=0.5:")
    print("-" * 80)

    for name, idx in gripper_indices.items():
        initial = initial_pos[idx].item()
        final = final_pos[idx].item()
        delta = final - initial

        marker = ""
        if name == "finger_joint":
            marker = " <-- COMMANDED"
        elif abs(delta) > 0.01:
            marker = " <-- MOVED! (likely mimic)"
        else:
            marker = " <-- No movement"

        print(f"  {name:30s}: {initial:7.3f} → {final:7.3f} (Δ={delta:+7.3f}){marker}")

    # Conclusions
    print_sep("CONCLUSIONS")

    moved_joints = []
    for name, idx in gripper_indices.items():
        if name != "finger_joint":
            delta = abs(final_pos[idx].item() - initial_pos[idx].item())
            if delta > 0.01:
                moved_joints.append(name)

    if moved_joints:
        print(f"\n✓ The following joints moved when finger_joint was commanded:")
        for name in moved_joints:
            print(f"  - {name}")
        print("\n  → These are likely MIMIC joints (automatically coupled to finger_joint)")
        print("  → You do NOT need to actuate them separately")
        print("  → Your current config is CORRECT")
    else:
        print(f"\n✗ No other joints moved when finger_joint was commanded!")
        print("\n  → These joints are INDEPENDENT")
        print("  → You NEED to add them to your actuator configuration")
        print("  → This is why your gripper isn't working properly!")

        print("\n  REQUIRED FIX:")
        print("  Add all gripper joints to the actuator:")
        print("""
        "gripper": ImplicitActuatorCfg(
            joint_names_expr=["finger_joint", "left_inner_knuckle_joint", 
                            "right_inner_knuckle_joint", "right_outer_knuckle_joint",
                            "left_outer_finger_joint", "right_outer_finger_joint"],
            # ... same settings ...
        ),
        """)

    print_sep("END")

    simulation_app.close()


if __name__ == "__main__":
    inspect_gripper_joints()