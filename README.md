<div align="center">

# ACE

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/illyshaieb/ACE/continuous-integration) ![GitHub repo size](https://img.shields.io/github/repo-size/illyshaieb/ace) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/4304d43af0004b7ba2e998565a1b31fb)](https://www.codacy.com/gh/IllyShaieb/ACE/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=illyshaieb/ACE&amp;utm_campaign=Badge_Grade) [![made-with-python](https://img.shields.io/badge/made%20with-Python-1f425f.svg)](https://www.python.org/) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/illyshaieb/ace?color=yellow) ![GitHub last commit](https://img.shields.io/github/last-commit/illyshaieb/ace) ![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/illyshaieb/ace?color=white&label=latest%20release)

</div>

ACE, the Artificial Consciousness Engine, is a digital assistant. It is designed to help you with your daily tasks and keep you in the loop with your life and the world.

## Getting Started

### Prerequisites
Please make sure you have the following installed:

| Package | Version | Description | Required |
| --- | --- | --- | --- |
| Python | 3.9+ | https://www.python.org/downloads/ | :heavy_check_mark: |
| Poetry | 1.0+ | https://python-poetry.org/ | :heavy_check_mark: |
| Git | 2.27+ | https://git-scm.com/ | :heavy_check_mark: |
| GitHub CLI | 2.7+ | https://github.com/cli/cli | :x: |

### Installation
First, navigate to a directory of your choice and run one of the following commands:
- Git

    ```bash
    $ git clone https://github.com/IllyShaieb/ACE.git
    ```

- GitHub CLI

    ```shell
    $ gh clone IllyShaieb/ACE
    ```

Then run the following commands to install the dependencies:

```shell
$ cd ACE
$ poetry install
```

### Running
To start ACE, run the following command:

```shell
$ poetry run python main.py
```

## Features
| | Intent | Description | Example |
| --- | --- | --- | --- |
| :wave: | greeting | respond with a greeting message | hello |
| :runner: | goodbye | respond with a goodbye message and then exit| goodbye |
