import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from models import SceneState, TransformationEngine

def test_transformation_engine():
    initial_state = SceneState(
        node_id="node_000",
        parent_id=None,
        seed=42,
        objects=[]
    )

    # Apply add_object transformation
    params_add = {
        "id": "obj_1",
        "type": "cube",
        "color": "red",
        "size": 1.0,
        "position": [0, 0, 0]
    }
    state_after_add = TransformationEngine.add_object(initial_state, params_add)

    # Apply change_color transformation
    params_color = {
        "id": "obj_1",
        "color": "blue"
    }
    state_after_color = TransformationEngine.change_color(state_after_add, params_color)

    # Serialize the final state to JSON
    final_state_json = json.dumps(state_after_color, default=lambda o: o.__dict__, indent=4)
    print("Final Scene State:")
    print(final_state_json)

if __name__ == "__main__":
    test_transformation_engine()