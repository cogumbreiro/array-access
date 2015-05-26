#!/bin/bash
find . -iname '*.c' -exec ./strip-lines.sh {} \; 
