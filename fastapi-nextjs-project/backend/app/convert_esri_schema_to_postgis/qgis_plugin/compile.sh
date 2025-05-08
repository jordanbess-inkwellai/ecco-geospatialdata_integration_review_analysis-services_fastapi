#!/bin/bash
# This file compiles the resources.qrc to resources.py
python3 -m PyQt5.pyrcc_main resources.qrc -o resources.py
