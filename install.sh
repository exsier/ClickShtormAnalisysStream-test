#!/bin/bash
python -m pip install --upgrade pip
pip3 install req.txt
pip3 install --upgrade torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116