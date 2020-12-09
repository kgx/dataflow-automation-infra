#!/bin/sh -l

echo "Hello $1"
#time=$(date)
#echo "::set-output name=time::$time"
echo "list files"
ls
echo "------"

git clone --depth 1 --branch feature/add_workflow --filter=blob:none --no-checkout https://github.com/maikelpenz/dataflow-sample-workflow.git
cd dataflow-sample-workflow
git checkout feature/add_workflow -- workflow
ls