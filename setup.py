from setuptools import find_packages, setup

setup(
    name="hermes",
    version="0.1.0",
    packages=find_packages(include=["PromptParser", "PromptParser.*"]),
    install_requires=[
        # Add your dependencies here
    ],
)
