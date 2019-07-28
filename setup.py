from pathlib import Path
from setuptools import setup


# current_folder = Path.cwd()
# requirements_path = current_folder / "requirements/base.txt"
# try:
#     with requirements_path.open() as f:
#         requires = [
#             line.strip()
#             for line in f.readlines()
#             if line.strip() != "" and not line.strip().startswith("#")
#         ]
# except FileNotFoundError:
#     pass

setup(
    name="microservice-flask",
    version="0.1",
    description="microservice-flask by learning from the book Python Microservices Development",
    url="https://github.com/copdips/microservice-flask",
    author="Xiang ZHU",
    author_email="xiang.zhu@outlook.com",
    license="MIT",
    packages=[],
    install_requires=["flask", "blinker"],
    # install_requires=requires,
    zip_safe=False,
)
