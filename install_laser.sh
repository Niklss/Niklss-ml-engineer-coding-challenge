git clone https://github.com/facebookresearch/LASER.git src/laser
export LASER=$PWD/src/laser
export PYTHONPATH="${PYTHONPATH}:${PWD}/src/laser/source"
bash src/laser/install_models.sh
bash src/laser/install_external_tools.sh