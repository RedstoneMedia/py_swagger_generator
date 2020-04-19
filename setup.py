import pathlib
from setuptools import setup, find_packages


HERE = pathlib.Path(__file__).parent


README = (HERE / "README.md").read_text()


setup(
    name="py-swagger-generator",
    version="1.0.2",
    description="A Package that can be used to create swagger yaml using templates",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/RedstoneMedia/py_swagger_generator",
    author="RedstoneMedia",
    keywords="swagger generator templates tool",
    license="GNU General Public License v3.0",
    packages=["swagger_generator"],
    include_package_data=True,
    install_requires=["PyYAML>=5.3.1", "PyInquirer>=1.0.3"],
    entry_points={
        "console_scripts": [
            "py-swagger-generator=swagger_generator.__main__:main",
        ]
    },
)