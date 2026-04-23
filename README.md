# Scene Generator

This project generates synthetic 3D scenes mimicking the exact visual style of the 2017 CLEVR dataset using BlenderProc.

## Setup

Ensure your environment includes `blenderproc` and `scipy`.

If you don't want to install Blender and dependencies locally, you can use Docker.

```bash
docker build -t clevr-gen .
```

## Running a Generation

You can pass a list of abstract objects with their physical properties.

### Example Script
```python
from models import SceneRequest, SceneObject
from scene_generator import SceneGenerator

generator = SceneGenerator(base_output_dir="output")

request = SceneRequest(
    scene_id="my_first_clevr_scene",
    object_rotation_unit="degrees",
    objects=[
        SceneObject(
            id="cube_1",
            shape="cube",
            color="red",
            size=1.0,
            material="Rubber",
            position=[-1.0, 0.0, 0.0],
            rotation=[0.0, 0.0, 35.0]
        ),
        SceneObject(
            id="sphere_1",
            shape="sphere",
            color="blue",
            size=1.0,
            material="Metal",
            position=[1.0, -1.0, 0.0],
            rotation=[0.0, 0.0, 0.0]
        )
    ]
)

out_dir = generator.generate(request)
print(f"Check your output image at: {out_dir}/my_first_clevr_scene.png")
```

A script using the generator has to be run with `blenderproc run` command.

The above payload will output a single 320x240 `.png` image along with its corresponding properties in a metadata `.json` file in the automatically generated output directory.

