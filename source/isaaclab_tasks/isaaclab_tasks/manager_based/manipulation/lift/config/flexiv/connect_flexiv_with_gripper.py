# patch_flexiv_usd_v2.py
import os
from isaaclab.app import AppLauncher

# Launch Isaac Sim
app_launcher = AppLauncher(headless=True)
simulation_app = app_launcher.app

import omni.usd
from pxr import Usd, UsdPhysics, Gf


def main():
    # INPUT PATH
    original_usd = "/home/mohamad/Research/IsaacLab/source/isaaclab_assets/isaaclab_assets/robots/data/flexiv/Rizon4s_with_Grav.usd"
    # OUTPUT PATH
    patched_usd = "/home/mohamad/Research/IsaacLab/source/isaaclab_assets/isaaclab_assets/robots/data/flexiv/Rizon4s_with_Grav_FIXED.usd"

    if not os.path.exists(original_usd):
        print(f"[ERROR] Input file not found: {original_usd}")
        simulation_app.close()
        return

    print(f"[INFO] Opening USD Stage: {original_usd}")
    # Open the stage so we can edit it
    omni.usd.get_context().open_stage(original_usd)
    stage = omni.usd.get_context().get_stage()

    if not stage:
        print("[ERROR] Failed to open stage.")
        simulation_app.close()
        return

    # ---------------------------------------------------------
    # 1. FIX ZERO MASS (The cause of explosion)
    # ---------------------------------------------------------
    # These prims were identified as having 0.0 mass
    zero_mass_prims = [
        "/Rizon4s/Grav_gripper/left_finger_tip",
        "/Rizon4s/Grav_gripper/right_finger_tip",
        "/Rizon4s/Grav_gripper/left_finger_mount",
        "/Rizon4s/Grav_gripper/right_finger_mount",
        "/Rizon4s/flange"
    ]

    print("[INFO] Patching Mass Properties...")
    for prim_path in zero_mass_prims:
        prim = stage.GetPrimAtPath(prim_path)
        if prim.IsValid():
            # Apply MassAPI if missing
            if not prim.HasAPI(UsdPhysics.MassAPI):
                UsdPhysics.MassAPI.Apply(prim)

            mass_api = UsdPhysics.MassAPI(prim)

            # Set valid mass (0.05 kg) and inertia
            # This prevents the "Divide by Zero" explosion in PhysX
            mass_api.CreateMassAttr(0.05)
            mass_api.CreateDiagonalInertiaAttr(Gf.Vec3f(0.0001, 0.0001, 0.0001))
            mass_api.CreateCenterOfMassAttr(Gf.Vec3f(0, 0, 0))
            print(f"   -> Fixed Mass for: {prim_path}")
        else:
            print(f"   [WARNING] Prim not found: {prim_path}")

    # ---------------------------------------------------------
    # 2. REMOVE HOSTILE DRIVES (The cause of "shaking")
    # ---------------------------------------------------------
    # The USD has a stiff controller (stiffness=10000) built-in.
    # We disable it so Isaac Lab RL can control the gripper.
    joint_path = "/Rizon4s/Grav_gripper/finger_joint"
    prim = stage.GetPrimAtPath(joint_path)

    if prim.IsValid():
        print(f"[INFO] Disabling built-in DriveAPI on: {joint_path}")
        # We disable the built-in drive by setting stiffness/damping to 0
        drive = UsdPhysics.DriveAPI.Get(prim, "angular")
        if not drive:
            drive = UsdPhysics.DriveAPI.Get(prim, "linear")

        if drive:
            drive.CreateStiffnessAttr(0.0)
            drive.CreateDampingAttr(0.0)
            print("   -> Drive Disabled.")

    # ---------------------------------------------------------
    # 3. SAVE
    # ---------------------------------------------------------
    print(f"[INFO] Saving fixed USD to: {patched_usd}")

    # We simply export the root layer to the new file.
    # This avoids the complex TransferContent() error you saw.
    try:
        stage.GetRootLayer().Export(patched_usd)
        print("[SUCCESS] File saved successfully.")
        print("IMPORTANT: Now update your 'flexiv.py' to point to this _FIXED.usd file.")
    except Exception as e:
        print(f"[ERROR] Failed to save: {e}")

    simulation_app.close()


if __name__ == "__main__":
    main()