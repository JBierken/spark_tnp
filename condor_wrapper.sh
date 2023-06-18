#!/bin/bash
echo "Setting up environment"
ReplaceMe_by_cdWorkdir
source env.sh
echo "Setup complete"
echo "Will run:"
echo "$@"
eval "$@"
