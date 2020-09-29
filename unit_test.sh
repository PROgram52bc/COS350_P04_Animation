#!/bin/bash
for reference in references/*.ppm; do
	filename=${reference#*/}
	if [ ! -f images/$filename ]; then
		echo "SKIP: $filename not generated"
	elif diff images/$filename $reference > /dev/null; then
		echo "PASS: $filename identical with reference"
	else
		echo "FAIL: $filename differs with reference"
	fi
done
