@echo off

set PYTHON=
set GIT=
set VENV_DIR=
set COMMANDLINE_ARGS= --xformers --api  --skip-version-check --skip-python-version-check --listen --port 7862

call webui.bat
