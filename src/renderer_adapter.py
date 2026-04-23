import os
import json
import math
import blenderproc as bproc
import bpy
from scipy.spatial.transform import Rotation as R
from PIL import Image
from models import SceneRequest

class RendererAdapter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        bproc.init()
        bproc.renderer.set_max_amount_of_samples(512)

        bpy.context.scene.cycles.blur_glossy = 2.0
        bpy.context.scene.cycles.transparent_min_bounces = 8
        bpy.context.scene.cycles.transparent_max_bounces = 8

        bproc.renderer.set_light_bounces(  
            diffuse_bounces=8,
            glossy_bounces=1,  
            max_bounces=12,  
            ao_bounces_render=3  
        )

    def render(self, scene_request: SceneRequest):
        bproc.clean_up(clean_up_camera=True)

        for world in bpy.data.worlds:
            world.use_nodes = True
            nodes = world.node_tree.nodes
            nodes.clear() 
            
            bg_node = nodes.new(type="ShaderNodeBackground")
            bg_node.inputs[0].default_value = (0.1, 0.1, 0.1, 1.0)
            bg_node.inputs[1].default_value = 0.6 # Emission
            
            out_node = nodes.new(type="ShaderNodeOutputWorld")
            world.node_tree.links.new(bg_node.outputs[0], out_node.inputs[0])

        ground = bproc.object.create_primitive("PLANE")
        ground.set_scale([500.0, 500.0, 1.0])
        ground.set_location([0.0, 0.0, 0.0])
        
        ground_mat = bproc.material.create("ground_material")
        ground_mat.set_principled_shader_value("Base Color", [0.6, 0.6, 0.6, 1.0])
        ground_mat.set_principled_shader_value("Metallic", 0.0)
        ground_mat.set_principled_shader_value("Roughness", 1.0)
        ground.replace_materials(ground_mat)

        bproc.camera.set_resolution(320, 240)
        
        # Camera setup
        rotation_matrix = R.from_euler('xyz', [1.10932, 0.01082, 0.81493]).as_matrix()
        cam_pose = bproc.math.build_transformation_mat([7.48113, -6.50764, 5.34367], rotation_matrix)
        bproc.camera.add_camera_pose(cam_pose)

        multiplier = 3.0

        # Lighting setup
        light_key = bproc.types.Light()
        light_key.set_type("AREA")
        light_key.set_location([6.4467, -2.9052, 4.2584])
        light_key.set_energy(78.54 * multiplier)
        light_key.set_color([1.0, 0.932, 0.817])
        light_key.set_scale([0.5, 0.5, 0.5]) 
        light_key.blender_obj.data.shape = 'DISK'


        light_fill = bproc.types.Light()
        light_fill.set_type("AREA")
        light_fill.set_location([-4.6711, -4.0136, 3.0112])
        light_fill.set_energy(23.56 * multiplier)
        light_fill.set_color([0.762, 0.818, 1.0])
        light_fill.set_scale([0.5, 0.5, 0.5])
        light_fill.blender_obj.data.shape = 'DISK'

        light_back = bproc.types.Light()
        light_back.set_type("AREA")
        light_back.set_location([-1.1685, 2.6460, 5.8157])
        light_back.set_energy(39.27 * multiplier)
        light_back.set_color([1.0, 1.0, 1.0])
        light_back.set_scale([1.0, 1.0, 1.0])
        light_back.blender_obj.data.shape = 'DISK'

        color_map = {
            "gray": [0.345, 0.345, 0.345, 1.0], "red": [0.682, 0.118, 0.118, 1.0],
            "blue": [0.169, 0.224, 0.643, 1.0], "green": [0.129, 0.443, 0.231, 1.0],
            "brown": [0.345, 0.227, 0.133, 1.0], "purple": [0.322, 0.180, 0.435, 1.0],
            "cyan": [0.169, 0.541, 0.659, 1.0], "yellow": [0.686, 0.655, 0.141, 1.0]
        }

        with bpy.data.libraries.load("templates/materials/MyMetal.blend", link=False) as (data_from, data_to):
            if "Material" in data_from.materials:
                data_to.materials = ["Material"]
        base_metal_mat = bpy.data.materials.get("Material")

        if base_metal_mat:
            base_metal_mat.use_fake_user = True

        with bpy.data.libraries.load("templates/materials/Rubber.blend", link=False) as (data_from, data_to):
            if "BMD_Rubber_0004" in data_from.materials:
                data_to.materials = ["BMD_Rubber_0004"]
        base_rubber_mat = bpy.data.materials.get("BMD_Rubber_0004")

        if base_rubber_mat:
            base_rubber_mat.use_fake_user = True

        objects = []
        rotation_unit = scene_request.object_rotation_unit.lower()
        to_radians = rotation_unit != "radians"
        for obj in scene_request.objects:
            scale = obj.size
            
            if obj.shape.lower() == "cube":
                scale = obj.size / math.sqrt(2)
                loaded_objs = bproc.loader.load_blend("templates/shapes/SmoothCube_v2.blend")
                b_obj = loaded_objs[0]
                
            elif obj.shape.lower() == "sphere":
                loaded_objs = bproc.loader.load_blend("templates/shapes/Sphere.blend")
                b_obj = loaded_objs[0]
                
            elif obj.shape.lower() == "cylinder":
                loaded_objs = bproc.loader.load_blend("templates/shapes/SmoothCylinder.blend")
                b_obj = loaded_objs[0]
                
            else:
                continue

            b_obj.set_scale([scale, scale, scale])
            z_pos = scale * 1.0
            
            x_pos = obj.position[0] if len(obj.position) > 0 else 0.0
            y_pos = obj.position[1] if len(obj.position) > 1 else 0.0
            b_obj.set_location([x_pos, y_pos, z_pos])

            if obj.rotation and len(obj.rotation) == 3:
                rot = [float(v) for v in obj.rotation]
                if to_radians:
                    rot = [math.radians(v) for v in rot]
                b_obj.set_rotation_euler(rot)

            rgba = color_map.get(obj.color.lower(), [1, 1, 1, 1])
            
            if "metal" in obj.material.lower():
                if base_metal_mat:
                    new_mat = base_metal_mat.copy()
                    new_mat.name = f"Metal_{obj.id}"
                    new_mat.node_tree.nodes["Group"].inputs["Color"].default_value = rgba
            else:
                # Rubber
                if base_rubber_mat:
                    new_mat = base_rubber_mat.copy()
                    new_mat.name = f"Rubber_{obj.id}"
                    new_mat.node_tree.nodes["Rubber"].inputs["Color"].default_value = rgba

            if 'new_mat' in locals() and new_mat:
                b_obj.blender_obj.data.materials.clear()
                b_obj.blender_obj.data.materials.append(new_mat)

            objects.append(b_obj)

        data = bproc.renderer.render()

        json_file = os.path.join(self.output_dir, f"{scene_request.scene_id}_metadata.json")
        with open(json_file, "w") as f:
            f.write(json.dumps(scene_request, default=lambda o: o.__dict__, indent=4))

        image_file = os.path.join(self.output_dir, f"{scene_request.scene_id}.png")
        if data and "colors" in data and len(data["colors"]) > 0:
            rendered_img = data["colors"][0]
            Image.fromarray(rendered_img).save(image_file)

        print(f"Rendered {scene_request.scene_id}: {json_file}, {image_file}")

