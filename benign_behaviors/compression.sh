#!/bin/bash -u

path_to_compression_files="./benign_behaviors/compression_files/"
compressed_files="compressed_files.tar.gz"

while true; do

  # compress all files in directory with compression files using tar
  tar -czf "$compressed_files" "$path_to_compression_files"

  if [ $? -ne 0 ]; then
    echo "Compression failed"
  fi

  rm -f $compressed_files

  sleep 0.2

done
