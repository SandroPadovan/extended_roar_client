#!/bin/bash -u

path_to_compression_files="./benign_behaviors/compression_files/"

compressed_files="compressed_files.tar.gz"

# set duration to first command line argument, or to default value of 0
duration=${1-0}

if [ "$duration" -gt 0 ]; then
  echo "executing compression script for $duration seconds..."
  end_time=$((SECONDS + duration))
else
  echo "executing compression script without a limit duration..."
fi

while true; do

  # compress all files in directory with compression files
  tar -czf "$compressed_files" "$path_to_compression_files"

  if [ $? -eq 0 ]; then
    echo "Compression successful. Tarball saved as $compressed_files"
  else
    echo "Compression failed"
  fi

  rm -f $compressed_files

  sleep 0.2

  # end loop after duration elapsed
  if [ "$duration" -gt 0 ] && [ $SECONDS -ge $end_time ]; then
    break
  fi

done
