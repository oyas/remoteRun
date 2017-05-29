#!/bin/bash

echo "run!!"
touch data/result
uname -a | tee -a data/result
pwd | tee -a data/result
sleep 12
echo "finished"

