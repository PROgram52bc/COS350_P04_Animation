#!/bin/bash
diff -y --suppress-common-lines <(xxd images/$1) <(xxd references/$1) | less
