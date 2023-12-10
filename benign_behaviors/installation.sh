#!/bin/bash

path_to_requirements="./benign_behaviors/requirements.txt"

# create and activate virtual environment
echo "activating venv..."
python3 -m venv ./benign_behaviors/venv
source ./benign_behaviors/venv/bin/activate
echo "done"

while true; do

  # install requirements without caching
  echo "installing requirements..."
  pip install -r $path_to_requirements --no-cache-dir --quiet
  echo "done"

  # uninstall all packages
  echo "uninstalling everything..."
  pip freeze | xargs pip uninstall -y --quiet
  echo "done"

done
