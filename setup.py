""" Setup module for the TP-Timesheet package """
from setuptools import setup
from tp_timesheet import __version__ as version

REQUIREMENTS = [
    "Pillow~=9.2",
    "selenium~=4.4",
    "docker~=6.0",
    "croniter~=1.3",
    "python-crontab~=2.6",
    "workalendar~=16.4.0",
]
DEV_REQUIREMENTS = {
    "dev": [
        "pytest>=6.0.0",
        "pylint~=2.13",
        "black>=22.8",
    ]
}

with open("README.md", encoding="utf-8") as readme_file:
    LONG_DESCRIPTION = "".join(readme_file.readlines())

setup(
    name="tp-timesheet",
    version=version,
    url="https://github.com/ThorpeJosh/tp-timesheet",
    license="MIT",
    author="Joshua Thorpe",
    author_email="josh@thorpe.engineering",
    description="CLI tool to automate the submisison of tp timesheets",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    keywords=["automation", "timesheet", "cli", "executable"],
    packages=["tp_timesheet"],
    include_package_data=True,
    install_requires=REQUIREMENTS,
    extras_require=DEV_REQUIREMENTS,
    python_requires=">=3.6",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    entry_points={
        "gui_scripts": ["tp-timesheet=tp_timesheet.__main__:run"],
    },
)
