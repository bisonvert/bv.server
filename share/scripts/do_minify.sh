#/bin/bash

for f in `cat file_list.txt`
do
    python jsmin.py < $f.js > $f-min.js
done
