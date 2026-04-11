from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
import hashlib

@dataclass
class SceneObject:
    id: str
    type: str
    color: str
    size: float
    position: List[float]

@dataclass
class SceneState:
    node_id: str
    parent_id: Optional[str]
    seed: int
    objects: List[SceneObject] = field(default_factory=list)

    def compute_hash(self) -> str:
        """Computes a deterministic hash of the visual state, ignoring object creation order."""
        if not self.objects:
            return hashlib.md5(b"empty_state").hexdigest()
            
        # 1. Sort objects by position (X, Y, Z) to guarantee order independence
        sorted_objs = sorted(
            self.objects, 
            key=lambda o: (o.position[0], o.position[1], o.position[2])
        )
        
        # 2. Create a standardized string representation of the scene
        obj_strings = [
            f"{o.type}_{o.color}_{o.size}_{o.position[0]}_{o.position[1]}_{o.position[2]}" 
            for o in sorted_objs
        ]
        state_string = "|".join(obj_strings)
        
        # 3. Hash it
        return hashlib.md5(state_string.encode('utf-8')).hexdigest()

@dataclass
class Edge:
    from_node: str
    to_node: str
    transformation: str
    params: Dict[str, Any]

@dataclass
class TreeGraph:
    dataset_name: str
    root_node: str
    edges: List[Edge] = field(default_factory=list)

class TransformationEngine:
    @staticmethod
    def add_object(state: SceneState, params: Dict[str, Any]) -> SceneState:
        new_objects = state.objects.copy()
        new_object = SceneObject(
            id=params['id'],
            type=params['type'],
            color=params['color'],
            size=params['size'],
            position=params['position']
        )
        for obj in new_objects:
            if obj.position == new_object.position:
                raise ValueError("Collision detected at position {}".format(new_object.position))
        new_objects.append(new_object)
        return SceneState(
            node_id=state.node_id,
            parent_id=state.parent_id,
            seed=state.seed,
            objects=new_objects
        )

    @staticmethod
    def change_color(state: SceneState, params: Dict[str, Any]) -> SceneState:
        new_objects = []
        for obj in state.objects:
            if obj.id == params['id']:
                new_objects.append(SceneObject(
                    id=obj.id,
                    type=obj.type,
                    color=params['color'],
                    size=obj.size,
                    position=obj.position
                ))
            else:
                new_objects.append(obj)
        return SceneState(
            node_id=state.node_id,
            parent_id=state.parent_id,
            seed=state.seed,
            objects=new_objects
        )

def serialize_scene_state(state: SceneState) -> str:
    return json.dumps(state, default=lambda o: o.__dict__, indent=4)

def serialize_tree_graph(graph: TreeGraph) -> str:
    return json.dumps(graph, default=lambda o: o.__dict__, indent=4)