#!/bin/bash

# Print all environment variables
env

# Start Hypercorn
hypercorn app.main:app --bind 0.0.0.0:$PORT
