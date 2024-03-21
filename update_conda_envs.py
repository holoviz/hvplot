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

# Remove ibis-duck from the Python 3.12 env since it's python-duck
# is not yet available on Python 3.12
# https://github.com/conda-forge/python-duckdb-feedstock/issues/98
fname = "envs/py3.12-tests.yaml"
with open(fname, "r", encoding="utf-8") as f:
    lines = f.readlines()

modified_lines = [line for line in lines if "ibis-duckdb" not in line]

with open(fname, "w") as f:
    f.writelines(modified_lines)
