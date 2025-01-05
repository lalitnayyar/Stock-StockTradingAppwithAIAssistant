import os
import shutil
from pathlib import Path

# Create build directory
build_dir = Path('build_output')
if build_dir.exists():
    shutil.rmtree(build_dir)
build_dir.mkdir()

# Files to copy
files_to_copy = [
    'app.py',
    'start.py',
    'worker.js',
    'requirements.txt',
    '.env',
    'wrangler.toml'
]

# Copy files
for file in files_to_copy:
    if Path(file).exists():
        shutil.copy2(file, build_dir)

# Create static directory
static_dir = build_dir / 'static'
static_dir.mkdir(exist_ok=True)

print("Build completed successfully!")
