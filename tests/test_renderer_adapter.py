import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from models import SceneRequest, SceneObject
from renderer_adapter import RendererAdapter

def test_renderer_adapter():
    output_dir = "test_output"

    renderer = RendererAdapter(output_dir)

    test_request = SceneRequest(
        scene_id="scene_000",
        object_rotation_unit="degrees",
        objects=[
            SceneObject(
                id="obj_1",
                shape="cube",
                color="red",
                size=1.0,
                material="Rubber",
                position=[0.0, 0.0, 0.0],
                rotation=[0.0, 0.0, 45.0]
            )
        ]
    )

    renderer.render(test_request)

if __name__ == "__main__":
    test_renderer_adapter()
