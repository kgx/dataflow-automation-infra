#!/bin/sh -l

# set variables
git_url=$1
branch_name=$2
commit_sha=$3
workflow_path=$4
git_url_basename=$(basename $git_url)
repository_name=${git_url_basename%.*}

echo $git_url
echo $branch_name
echo $commit_sha
echo $workflow_path
echo $git_url_basename
echo $repository_name

# clone workflow into container
git clone --branch $branch_name \
         --no-checkout $git_url
cd $repository_name

git checkout $commit_sha --$workflow_path

ls