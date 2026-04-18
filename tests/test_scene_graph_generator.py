import blenderproc as bproc
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from scene_graph_generator import SceneGraphGenerator


def test_scene_generator():
    max_depth = 2
    branches_per_node = 2
    generator = SceneGraphGenerator(base_output_dir="test_output")
    run_dir = generator.generate(max_depth=max_depth, branches_per_node=branches_per_node, seed=42)

    if branches_per_node == 1:
        expected_node_count = max_depth + 1
    else:
        expected_node_count = (branches_per_node ** (max_depth + 1) - 1) // (branches_per_node - 1)

    expected_files = ["tree_graph.json"]
    for node_idx in range(expected_node_count):
        node_id = f"node_{node_idx:03d}"
        expected_files.append(f"{node_id}.png")
        expected_files.append(f"{node_id}_state.json")

    missing = [
        filename
        for filename in expected_files
        if not os.path.exists(os.path.join(run_dir, filename))
    ]

    if missing:
        raise AssertionError(f"Missing expected output files: {missing}")

    print("Tree generation test passed.")
    print(f"Output directory: {run_dir}")


if __name__ == "__main__":
    test_scene_generator()
