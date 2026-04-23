FROM python:3.10-slim

# Blendera dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libxrender1 \
    libxxf86vm1 \
    libxfixes3 \
    libxi6 \
    libxkbcommon0 \
    libsm6 \
    libxext6 \
    libglib2.0-0 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN pip install --upgrade pip
RUN pip install blenderproc scipy Pillow

COPY . .

RUN echo "import blenderproc as bproc\nprint('Installing Blender...')" > install_blender.py && \
    blenderproc run install_blender.py && \
    rm install_blender.py

RUN mkdir -p output

CMD ["blenderproc", "run", "tests/test_scene_generator.py"]