#!/usr/bin/env bash
source $(dirname $0)/activate_env.sh
if [[ -f "$cwd/bin/develop" ]];then
    cd "$cwd"
    $cwd/bin/develop up
    exit $?
fi
# vim:set et sts=4 ts=4 tw=80:
