import re
from pathlib import Path
from setuptools import find_packages, setup

with open(Path(__file__).parent / "dask_ecs_lib" / "__init__.py") as f:
    VERSION = re.compile(r".*__version__ = \"(.*?)\"", re.S).match(f.read()).group(1)

INSTALL_REQUIRES = (Path(__file__).parent / "requirements.txt").read_text().splitlines()

setup(
    name='dask_ecs_lib',
    packages=find_packages(include=['dask_ecs_lib']),
    version=VERSION,
    description='Dask ECS library',
    author='Richard',
    author_email='rich.olaniyan@gmail.com',
    python_requires=">=3.7",
    install_requires=INSTALL_REQUIRES,
    data_files=[("dask_ecs_lib", ["dask_ecs_lib/log.json"] )],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
    include_package_data=True
)

