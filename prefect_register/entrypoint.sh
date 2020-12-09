#!/bin/sh -l

echo "Hello $1"
#time=$(date)
#echo "::set-output name=time::$time"
echo "list files"
ls
echo "------"

git clone --branch feature/add_workflow --no-checkout https://github.com/maikelpenz/dataflow-sample-workflow.git
cd dataflow-sample-workflow
git checkout e678cd06ba5db1492b0297e5cd387aab029d3eaf -- workflow
ls
ls workflow