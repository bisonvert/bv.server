#!/usr/bin/env bash
source $(dirname $0)/activate_env.sh
# $project come via env.
# build all dependencies if not already installed
minimerge  -v --only-dependencies $minibuild
if [[ $? != 0 ]];then exit $?;fi
minimerge  -NRuv $minibuild
if [[ $? != 0 ]];then exit $?;fi 
# vim:set et sts=4 ts=4 tw=80:
