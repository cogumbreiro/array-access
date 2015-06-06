#!/bin/bash
for f in dataset-2/*.c.txt; do
    ./gen-dataset-3.py "$f" | target/release/array_access > "${f%.c.txt}.jsonl"
done
mv dataset-2/*.jsonl dataset-3
