#!/usr/bin/env python3
"""Fix: Correct handling of transform attributes for Flexiv and gripper."""

from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": False})  # Set to False to debug in Isaac Sim GUI

import omni.usd
from pxr import Usd, UsdGeom, UsdPhysics, Sdf, Gf
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.storage.native import get_assets_root_path

# Paths to USD files
assets_root = get_assets_root_path()
FLEXIV_USD = f"{assets_root}/Isaac/Robots/Flexiv/Rizon4/flexiv_rizon4.usd"
ROBOTIQ_USD = f"{assets_root}/Isaac/Robots/Robotiq/2F-85/Robotiq_2F_85_flattened.usd"

# Path for the combined USD file
EXPORT_PATH = "/home/mohamad/Research/IsaacLab/source/isaaclab_assets/isaaclab_assets/robots/data/flexiv/flexiv_rizon4_with_Robotiq_2F_85_flattened.usd"

# Create new stage
omni.usd.get_context().new_stage()
stage = omni.usd.get_context().get_stage()

# 1. Add Flexiv to the stage
FLEXIV_PATH = "/World/Flexiv"
add_reference_to_stage(usd_path=FLEXIV_USD, prim_path=FLEXIV_PATH)

# 2. Add Robotiq gripper to the stage
GRIPPER_PATH = "/World/Flexiv/Gripper"
add_reference_to_stage(usd_path=ROBOTIQ_USD, prim_path=GRIPPER_PATH)

# 3. Attach the gripper to the Flexiv flange
FLANGE_PATH = f"{FLEXIV_PATH}/flange"  # Flexiv's end-effector frame
GRIPPER_BASE_PATH = f"{GRIPPER_PATH}/Robotiq_2F_85/base_link"  # Gripper's base link

# Check gripper base link exists
gripper_base_prim = stage.GetPrimAtPath(GRIPPER_BASE_PATH)
if not gripper_base_prim.IsValid():
    raise RuntimeError(f"Gripper base link does NOT exist: {GRIPPER_BASE_PATH}")

# Create fixed joint to attach the gripper to the Flexiv flange
fixed_joint_path = f"{FLEXIV_PATH}/gripper_fixed_joint"
stage.DefinePrim(fixed_joint_path, "PhysicsFixedJoint")

fixed_joint = UsdPhysics.FixedJoint(stage.GetPrimAtPath(fixed_joint_path))
fixed_joint.GetBody0Rel().SetTargets([Sdf.Path(FLANGE_PATH)])  # Connect to Flexiv flange
fixed_joint.GetBody1Rel().SetTargets([Sdf.Path(GRIPPER_BASE_PATH)])  # Connect to gripper base
print(f"✓ Created fixed joint between Flexiv flange and gripper base: {fixed_joint_path}")

# 4. Adjust robot and gripper positions for verification
print("\nCentering Flexiv and gripper in the scene...")

def set_translate_and_rotate(prim, translate=(0.0, 0.0, 0.0), rotate=(0.0, 0.0, 0.0)):
    """Set translate and rotateXYZ attributes on the prim if it is Xformable."""
    if not prim.IsA(UsdGeom.Xform):
        print(f"✗ Prim at {prim.GetPath()} is not Xformable. Skipping transformations.")
        return

    xformable = UsdGeom.Xformable(prim)

    # Set translate
    translate_attr = prim.GetAttribute("xformOp:translate")
    if translate_attr.IsValid():
        translate_attr.Set(Gf.Vec3f(*translate))
    else:
        xformable.AddTranslateOp().Set(Gf.Vec3f(*translate))

    # Set rotateXYZ
    rotate_attr = prim.GetAttribute("xformOp:rotateXYZ")
    if rotate_attr.IsValid():
        rotate_attr.Set(Gf.Vec3f(*rotate))
    else:
        xformable.AddRotateXYZOp().Set(Gf.Vec3f(*rotate))


# Ensure transform attributes and adjust transforms
flexiv_prim = stage.GetPrimAtPath(FLEXIV_PATH)
set_translate_and_rotate(flexiv_prim, translate=(0.0, 0.0, 0.0), rotate=(0.0, 0.0, 0.0))

gripper_prim = stage.GetPrimAtPath(GRIPPER_PATH)
set_translate_and_rotate(gripper_prim, translate=(0.0, 0.0, 0.0), rotate=(0.0, 0.0, 0.0))

# 5. Adjust the camera to focus on the robot
print("\nAdjusting camera to focus on the robot...")
camera_path = "/OmniverseKit_Persp"
camera_prim = stage.GetPrimAtPath(camera_path)
if camera_prim.IsValid():
    set_translate_and_rotate(camera_prim, translate=(0.0, -2.0, 1.5), rotate=(30.0, 0.0, 0.0))

# 6. Save the combined robot to USD
stage.GetRootLayer().Export(EXPORT_PATH)
print(f"\n✓ Combined Flexiv + Gripper setup saved to: {EXPORT_PATH}")

# Keep the simulation open for inspection
print("\nScene created successfully. Keeping window open for 30 seconds.")
for _ in range(300):  # Keep the window active for inspection
    simulation_app.update()

simulation_app.close()