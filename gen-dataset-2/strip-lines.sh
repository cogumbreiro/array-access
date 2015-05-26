#!/bin/bash
cat "$1" | grep '\]\[' | cut -d= -f1 > "$1.txt"
