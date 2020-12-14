#!/bin/sh -l

# set variables
git_url=$1
branch_name=$2
commit_sha=$3
workflow_path=$4
git_url_basename=$(basename $git_url)
repository_name=${git_url_basename%.*}

# clone workflow into container
git clone --branch $branch_name \
         --no-checkout $git_url

cd $repository_name
git checkout $commit_sha -- $workflow_path

# move to /tmp/
mv $workflow_path /tmp/$workflow_path
# move flow register into the flow folder
mv /tmp/workflow_register.py /tmp/$workflow_path/workflow_register.py

# install prefect
pip3 install prefect

# register workflow
python3 /tmp/$workflow_path/workflow_register.py


