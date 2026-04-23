from dataclasses import dataclass, field
from typing import List
import json

@dataclass
class SceneObject:
    id: str
    shape: str
    color: str
    size: float
    material: str
    position: List[float]
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])

@dataclass
class SceneRequest:
    scene_id: str
    object_rotation_unit: str = "degrees"
    objects: List[SceneObject] = field(default_factory=list)

def serialize_scene_request(request: SceneRequest) -> str:
    return json.dumps(request, default=lambda o: o.__dict__, indent=4)
