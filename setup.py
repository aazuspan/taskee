from setuptools import find_packages, setup  # type: ignore

version = "0.0.1"

requirements = ["earthengine-api", "rich", "humanize", "notifypy", "requests", "click"]
test_requirements = ["pytest"]
dev_requirements = [
    "pre-commit",
    "black",
    "isort",
    "bumpversion",
    "twine",
    "mypy",
    "types-requests",
] + test_requirements
extras_require = {"dev": dev_requirements, "test": test_requirements}

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    name="taskee",
    version=version,
    description="Notifications for Earth Engine tasks.",
    long_description=readme + "\n\n",
    keywords="earth-engine, notifications, tasks, cli, command-line",
    author="Aaron Zuspan",
    author_email="aa.zuspan@gmail.com",
    url="https://github.com/aazuspan/taskee",
    license_files=("LICENSE",),
    license="GPLv3+",
    install_requires=requirements,
    tests_require=test_requirements,
    extras_require=extras_require,
    python_requires=">=3.7",
    test_suite="tests",
    packages=find_packages(),
    long_description_content_type="text/markdown",
    entry_points="""
        [console_scripts]
        taskee=taskee.cli.cli:main
    """,
)
