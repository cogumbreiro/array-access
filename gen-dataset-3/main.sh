#!/bin/bash
find dataset-2  -name "*.c.txt" -exec sh -c './gen-dataset-3.py "$1" > "${1%.c.txt}.jsonl"' _ {} \;
mv dataset-2/*.jsonl dataset-3
