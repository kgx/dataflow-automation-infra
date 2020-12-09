#!/bin/sh -l

git_url=$1
branch_name=$2
commit_sha=$3

git_url_basename=$(basename $git_url)
repository_name=${git_url_basename%.*}

#echo "Hello $1"
#time=$(date)
#echo "::set-output name=time::$time"

git clone --branch $branch_name \
         --no-checkout $git_url
cd $repository_name
git checkout $commit_sha -- workflow
ls

# git clone --branch feature/add_workflow --no-checkout https://github.com/maikelpenz/dataflow-sample-workflow.git
# cd dataflow-sample-workflow
# git checkout e678cd06ba5db1492b0297e5cd387aab029d3eaf -- workflow