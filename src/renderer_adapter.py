import os
import json
import numpy as np
import blenderproc as bproc
from PIL import Image
from models import SceneState

class RendererAdapter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        bproc.init()

    def render(self, scene_state: SceneState):
        # 1. Clean up the scene from any previous renders
        bproc.clean_up(clean_up_camera=True)

        # 2. Setup Camera
        location = np.array([0, -10, 6])
        poi = np.array([0, 0, 0])
        rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location)
        cam_pose = bproc.math.build_transformation_mat(location, rotation_matrix)
        
        bproc.camera.add_camera_pose(cam_pose)
        bproc.camera.set_resolution(512, 512)

        # 3. Setup Light
        light = bproc.types.Light()
        light.set_type("POINT")
        light.set_location([5, -5, 5])
        light.set_energy(1000)

        # 4. Map Colors
        color_map = {
            "red": [1, 0, 0, 1],
            "blue": [0, 0, 1, 1],
            "green": [0, 1, 0, 1],
            "yellow": [1, 1, 0, 1]
        }

        floor = bproc.object.create_primitive("PLANE", scale=[10, 10, 1], location=[0, 0, -0.5])
        floor_mat = bproc.material.create("floor_mat")
        floor_mat.set_principled_shader_value("Base Color", [0.8, 0.8, 0.8, 1.0])
        floor.add_material(floor_mat)

        # 5. Create objects from SceneState
        for obj in scene_state.objects:
            if obj.type.lower() == "cube":
                b_obj = bproc.object.create_primitive("CUBE")
                b_obj.set_scale([obj.size/2, obj.size/2, obj.size/2]) 
            elif obj.type.lower() == "sphere":
                b_obj = bproc.object.create_primitive("SPHERE")
                b_obj.set_scale([obj.size, obj.size, obj.size])
            else:
                continue 

            b_obj.set_location(obj.position)

            mat = bproc.material.create("mat_" + obj.id)
            rgba = color_map.get(obj.color.lower(), [1, 1, 1, 1])
            mat.set_principled_shader_value("Base Color", rgba)
            b_obj.add_material(mat)

        # 6. Render the scene
        data = bproc.renderer.render()

        # 7. Save Output
        state_file = os.path.join(self.output_dir, f"{scene_state.node_id}_state.json")
        with open(state_file, "w") as f:
            f.write(json.dumps(scene_state, default=lambda o: o.__dict__, indent=4))

        # Extract the rendered image and save as PNG
        image_file = os.path.join(self.output_dir, f"{scene_state.node_id}.png")
        rendered_img = data["colors"][0]
        Image.fromarray(rendered_img).save(image_file)

        print(f"Rendered {scene_state.node_id}: {state_file}, {image_file}")