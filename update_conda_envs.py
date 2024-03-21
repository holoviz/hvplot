import subprocess
from pathlib import Path

subprocess.run([
    "pyproject2conda",
    "project",
    "--overwrite",
    "force",
    "--template-python",
    str(Path('envs', 'py{py_version}-{env}')),
])

# Hacky way to install the package in editable mode when creating the env.
for file in Path('envs').glob('*.yaml'):
    with open(file, 'a', encoding='utf-8') as f:
        f.write('  - pip\n')
        f.write('  - pip:\n')
        f.write('    - -e ..\n')