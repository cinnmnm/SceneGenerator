import json
import os
from collections import deque
from datetime import datetime
from typing import Deque, Tuple

from models import Edge, SceneState, TransformationEngine, TreeGraph
from renderer_adapter import RendererAdapter


class TreeGenerator:
    def __init__(self, base_output_dir: str = "test_output"):
        self.base_output_dir = base_output_dir
        os.makedirs(self.base_output_dir, exist_ok=True)

    def _create_run_dir(self) -> Tuple[str, str]:
        dataset_name = datetime.now().strftime("run_%Y%m%d_%H%M%S_%f")
        run_dir = os.path.join(self.base_output_dir, dataset_name)
        os.makedirs(run_dir, exist_ok=False)
        return dataset_name, run_dir

    def _graph_payload(self, graph: TreeGraph) -> dict:
        return {
            "dataset_name": graph.dataset_name,
            "root_node": graph.root_node,
            "edges": [
                {
                    "from": edge.from_node,
                    "to": edge.to_node,
                    "transformation": edge.transformation,
                    "params": edge.params,
                }
                for edge in graph.edges
            ],
        }

    def generate(self, max_depth: int, branches_per_node: int, seed: int = 42) -> str:
        dataset_name, run_dir = self._create_run_dir()
        renderer = RendererAdapter(run_dir)

        root_state = SceneState(node_id="node_000", parent_id=None, seed=seed, objects=[])
        graph = TreeGraph(dataset_name=dataset_name, root_node=root_state.node_id)

        visited_states = {}
        visited_states[root_state.compute_hash()] = root_state.node_id
        
        renderer.render(root_state)

        queue: Deque[Tuple[SceneState, int]] = deque([(root_state, 0)])
        node_counter = 1
        colors = ["red", "blue", "green", "yellow"]
        object_types = ["cube", "sphere"]

        while queue:
            current_state, depth = queue.popleft()
            renderer.render(current_state)

            if depth >= max_depth:
                continue

            for branch_idx in range(branches_per_node):
                child_node_id = f"node_{node_counter:03d}"
                obj_id = f"obj_{child_node_id.split('_')[1]}"
                obj_type = object_types[(depth + branch_idx) % len(object_types)]
                color = colors[(depth + branch_idx) % len(colors)]
                position = [float(depth * 3 + branch_idx), 0.0, 0.0]

                params = {
                    "id": obj_id,
                    "type": obj_type,
                    "color": color,
                    "size": 1.0,
                    "position": position,
                }

                transformed = TransformationEngine.add_object(current_state, params)
                child_state = SceneState(
                    node_id=child_node_id,
                    parent_id=current_state.node_id,
                    seed=seed + node_counter,
                    objects=transformed.objects,
                )

                state_hash = child_state.compute_hash()

                if state_hash in visited_states:
                    existing_node_id = visited_states[state_hash]
                    graph.edges.append(
                        Edge(
                            from_node=current_state.node_id,
                            to_node=existing_node_id, 
                            transformation="add_object",
                            params={"type": obj_type, "color": color, "size": 1.0, "position": position}
                        )
                    )
                else:
                    visited_states[state_hash] = child_node_id
                    renderer.render(child_state)
                    
                    graph.edges.append(
                        Edge(
                            from_node=current_state.node_id,
                            to_node=child_node_id,
                            transformation="add_object",
                            params={"type": obj_type, "color": color, "size": 1.0, "position": position}
                        )
                    )
                    queue.append((child_state, depth + 1))
                    node_counter += 1

                graph.edges.append(
                    Edge(
                        from_node=current_state.node_id,
                        to_node=child_node_id,
                        transformation="add_object",
                        params={
                            "type": obj_type,
                            "color": color,
                            "size": 1.0,
                            "position": position,
                        },
                    )
                )

                queue.append((child_state, depth + 1))
                node_counter += 1

        graph_file = os.path.join(run_dir, "tree_graph.json")
        with open(graph_file, "w", encoding="utf-8") as f:
            json.dump(self._graph_payload(graph), f, indent=4)

        return run_dir
