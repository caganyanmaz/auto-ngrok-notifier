#!/bin/bash

file="$(realpath $0)"
path="$(dirname $file)"
source "$path/../.venv/bin/activate"
python "$path/main.py"
