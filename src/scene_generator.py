import os
from datetime import datetime
from models import SceneRequest
from renderer_adapter import RendererAdapter

class SceneGenerator:
    def __init__(self, base_output_dir: str = "output"):
        self.base_output_dir = base_output_dir
        os.makedirs(self.base_output_dir, exist_ok=True)

    def _create_run_dir(self) -> str:
        run_name = datetime.now().strftime("run_%Y%m%d_%H%M%S_%f")
        run_dir = os.path.join(self.base_output_dir, run_name)
        os.makedirs(run_dir, exist_ok=False)
        return run_dir

    def generate(self, request: SceneRequest) -> str:
        """
        Generate a single image and metadata JSON based on the isolated scene request.
        Outputs result to a unique run directory.
        """
        run_dir = self._create_run_dir()
        renderer = RendererAdapter(run_dir)
        renderer.render(request)
        return run_dir
