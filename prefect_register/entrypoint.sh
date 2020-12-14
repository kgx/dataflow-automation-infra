#!/bin/sh -l

# set variables
git_url=$1
branch_name=$2
commit_sha=$3
workflow_path=$4
git_url_basename=$(basename $git_url)
repository_name=${git_url_basename%.*}

echo "find . -name"
find . -name "workflow_register.py"

echo "pwd"
pwd

# clone workflow into container
git clone --branch $branch_name \
         --no-checkout $git_url
echo "ls"
ls         
cd $repository_name
git checkout $commit_sha -- $workflow_path
ls $workflow_path/