# inspect_robot_deep.py
import os
from isaaclab.app import AppLauncher

# Launch Isaac Sim
app_launcher = AppLauncher(headless=True)
simulation_app = app_launcher.app

import omni.usd
from pxr import Usd, UsdPhysics, UsdGeom, PhysxSchema, Gf


def main():
    # PATH
    usd_path = "/home/mohamad/Research/IsaacLab/source/isaaclab_assets/isaaclab_assets/robots/data/flexiv/Rizon4s_with_Grav.usd"

    if not os.path.exists(usd_path):
        print(f"[ERROR] Path not found: {usd_path}")
        simulation_app.close()
        return

    print(f"[INFO] Opening Stage: {usd_path}")
    omni.usd.get_context().open_stage(usd_path)
    stage = omni.usd.get_context().get_stage()

    print("\n" + "=" * 120)
    print(" 1. MASS PROPERTIES (Critical for Stability)")
    print("    If Mass < 0.01 or Inertia is near 0, simulation will explode.")
    print("=" * 120)
    print(f"{'LINK PATH':<60} | {'MASS':<10} | {'INERTIA DIAGONAL':<30}")
    print("-" * 120)

    for prim in stage.Traverse():
        if prim.HasAPI(UsdPhysics.MassAPI):
            mass_api = UsdPhysics.MassAPI(prim)
            mass = mass_api.GetMassAttr().Get()
            inertia = mass_api.GetDiagonalInertiaAttr().Get()

            # Format output
            m_str = f"{mass:.4f}" if mass is not None else "None"
            i_str = str(inertia) if inertia is not None else "None"

            print(f"{prim.GetPath().pathString:<60} | {m_str:<10} | {i_str:<30}")

    print("\n" + "=" * 120)
    print(" 2. JOINT DRIVES & MIMICS (Critical for Control)")
    print("    Check if joints have existing Stiffness/Damping or are Mimic joints.")
    print("=" * 120)
    print(f"{'JOINT NAME':<40} | {'TYPE':<10} | {'STIFFNESS':<10} | {'DAMPING':<10} | {'MIMIC?'}")
    print("-" * 120)

    for prim in stage.Traverse():
        if prim.IsA(UsdPhysics.Joint):
            path = prim.GetName()
            j_type = "Unknown"
            if prim.IsA(UsdPhysics.RevoluteJoint):
                j_type = "Revolute"
            elif prim.IsA(UsdPhysics.PrismaticJoint):
                j_type = "Prismatic"
            elif prim.IsA(UsdPhysics.FixedJoint):
                j_type = "Fixed"

            # Check Drive API
            stiffness = "N/A"
            damping = "N/A"
            # Usually drives are "angular" or "linear"
            if prim.HasAPI(UsdPhysics.DriveAPI):
                # Try getting the API for "angular" drive which is standard for revolute
                drive = UsdPhysics.DriveAPI.Get(prim, "angular")
                if not drive:
                    drive = UsdPhysics.DriveAPI.Get(prim, "linear")

                if drive:
                    s_attr = drive.GetStiffnessAttr().Get()
                    d_attr = drive.GetDampingAttr().Get()
                    stiffness = f"{s_attr:.1f}" if s_attr is not None else "None"
                    damping = f"{d_attr:.1f}" if d_attr is not None else "None"

            # Check Mimic API
            mimic = "No"
            if prim.HasAPI(PhysxSchema.PhysxMimicJointAPI):
                mimic = "YES"

            print(f"{path:<40} | {j_type:<10} | {stiffness:<10} | {damping:<10} | {mimic}")

    print("\n" + "=" * 120)
    print(" 3. COLLISION MESHES")
    print("    Check if tip links have collision meshes that might hit the table.")
    print("=" * 120)

    for prim in stage.Traverse():
        if prim.HasAPI(UsdPhysics.CollisionAPI):
            # Check if it's a mesh
            is_mesh = prim.IsA(UsdGeom.Mesh)
            parent = prim.GetParent().GetName()
            print(f"Collision Prim: {prim.GetName():<30} (Parent: {parent})")

    simulation_app.close()


if __name__ == "__main__":
    main()