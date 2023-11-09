#!/bin/bash

set -eu

TARGET_DIR=$(readlink -f "$HOME/.csstuning/dbms/mysql_data/benchbase")

TOTAL_SIZE=$((44 * 1048576))

TOTAL_SIZE_GiB=$(bc <<<"scale=2; $TOTAL_SIZE/1048576")

echo "Monitoring the size of $TARGET_DIR"

PREV_SIZE=$(du -sk "$TARGET_DIR" | cut -f1)
START_TIME=$(date +%s)

while [[ "$PREV_SIZE" -lt "$TOTAL_SIZE" ]]; do
  CURRENT_SIZE=$(du -sk "$TARGET_DIR" | cut -f1)

  # Calculate size difference
  SIZE_DIFF=$((CURRENT_SIZE - PREV_SIZE))
  SIZE_DIFF_MB=$(bc <<<"scale=2; $SIZE_DIFF/1024")

  # Get current time and calculate elapsed time
  CURRENT_TIME=$(date +%s)
  ELAPSED_TIME=$((CURRENT_TIME - START_TIME))

  # Avoid division by zero error
  if [[ "$ELAPSED_TIME" -eq 0 ]]; then
    ELAPSED_TIME=1
  fi

  # Calculate speed (GiB/s)
  SPEED=$(bc <<<"scale=2; $SIZE_DIFF_MB/$ELAPSED_TIME")

  # Calculate progress
  PROGRESS=$(bc <<<"scale=2; ($CURRENT_SIZE/$TOTAL_SIZE)*100")

  # Calculate estimated remaining time (s)
  REMAINING_SIZE=$((TOTAL_SIZE - CURRENT_SIZE))
  if [[ "$SIZE_DIFF" -gt 0 ]]; then
    ESTIMATED_TIME=$(bc <<<"scale=0; $REMAINING_SIZE/$SIZE_DIFF*$ELAPSED_TIME")
  else
    ESTIMATED_TIME=0
  fi

  # Convert estimated time to human-readable format
  if [[ "$ESTIMATED_TIME" -gt 0 ]]; then
    ETA=$(date -ud "@$ESTIMATED_TIME" +'%H:%M:%S')
  else
    ETA="N/A"
  fi

  # Convert current size to GiB for display purposes
  CURRENT_SIZE_GiB=$(bc <<<"scale=2; $CURRENT_SIZE/1048576")

  # Display current status
  echo -ne "Current size: $CURRENT_SIZE_GiB GiB / $TOTAL_SIZE_GiB GiB ($PROGRESS%) - Speed: $SPEED MB/s - ETA: $ETA\\r"

  # Update PREV_SIZE and START_TIME for the next loop iteration
  PREV_SIZE=$CURRENT_SIZE
  START_TIME=$CURRENT_TIME

  sleep 5
done

echo -ne "\\n"
echo "Monitor done."
