#!/bin/bash
echo "Setting up environment"
cd /afs/cern.ch/user/j/jbierken/spark_tnp
source env.sh
echo "Setup complete"
echo "Will run:"
echo "$@"
eval "$@"
