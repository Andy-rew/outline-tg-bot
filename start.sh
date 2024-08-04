#!/bin/bash

cd code || exit
python ../init_db.py
python ../run.py
