#!/usr/bin/env bash

# The first argument gives the path of the Enron Corpus
# The second argument gives the path of the

find $1 -type f | grep -v "all_documents" | grep -v ".DS_Store" > $2