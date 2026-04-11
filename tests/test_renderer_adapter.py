import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from models import SceneState
from renderer_adapter import RendererAdapter

def test_renderer_adapter():
    output_dir = "test_output"

    renderer = RendererAdapter(output_dir)

    test_state = SceneState(
        node_id="node_000",
        parent_id=None,
        seed=155868,
        objects=[
            {
                "id": "obj_1",
                "type": "cube",
                "color": "red",
                "size": 1.0,
                "position": [0, 0, 0]
            }
        ]
    )

    renderer.render(test_state)

if __name__ == "__main__":
    test_renderer_adapter()