import blenderproc as bproc
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from models import SceneRequest, SceneObject
from scene_generator import SceneGenerator

def test_scene_generator():
    generator = SceneGenerator("test_output")

    test_request = SceneRequest(
        scene_id="clevr_reproduction_test",
        object_rotation_unit="degrees",
        objects=[
            SceneObject(
                id="obj_01_large_cube",
                shape="cube",
                color="red",
                size=1.0,
                material="Metal",
                position=[-1.5, -1.0, 0.0],
                rotation=[0.0, 0.0, 35.0]
            ),
            SceneObject(
                id="obj_02_small_sphere",
                shape="sphere",
                color="cyan",
                size=0.5,
                material="Metal",
                position=[1.2, 0.5, 0.0],
                rotation=[0.0, 0.0, 0.0]
            ),
            SceneObject(
                id="obj_03_large_cylinder",
                shape="cylinder",
                color="purple",
                size=1.0,
                material="Metal",
                position=[0.0, 2.0, 0.0],
                rotation=[0.0, 0.0, 90.0]
            ),
            SceneObject(
                id="obj_04_small_cube",
                shape="cube",
                color="red",
                size=0.5,
                material="Rubber",
                position=[2.0, -2.0, 0.0],
                rotation=[0.0, 0.0, -30.0]
            )
        ]
    )

    out_dir = generator.generate(test_request)
    print(f"Generated successfully in {out_dir}")

if __name__ == "__main__":
    test_scene_generator()
