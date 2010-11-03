#!/usr/bin/env bash
source $(dirname $0)/activate_env.sh
# add packages to be tested here
# run testrunner on each
for i in $tested_packages;do
    $test_command -x -m "$i"
done
# copy test reports to workspace as the reporter want relative paths
reportsdir="$WORKSPACE/testhudsonxmlreports"
if [[ -d $reportsdir ]];then
    rm -rf $reportsdir
fi 
mkdir $reportsdir
# $xmlreports come with activate_env
testi=0
for d in $xmlreports;do
    testi=$(($testi+1))
    mkdir "$reportsdir/$testi"
    cp -rf "$d/"*.xml "$reportsdir/$testi"
done
# vim:set et sts=4 ts=4 tw=80:
