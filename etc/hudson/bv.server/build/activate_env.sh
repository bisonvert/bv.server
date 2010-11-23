#!/usr/bin/env bash
# install .env if in minitage
cwd="/opt/minitage/django/bv.server-prod"
project="bv.server"
test_command="/opt/minitage/django/bv.server-prod/bin/bvserver.test"
category="$(basename $(dirname $(dirname $cwd)))"
minibuild="$(basename $cwd)"
hudson=$cwd/etc/hudson
envfile=$cwd/sys/share/minitage/minitage.env
mcfg=$ins/../../etc/minimerge.cfg
if [[ -f $mcfg ]];then
    if [[ ! -e $envfile ]];then    
        easy_install -U minitage.paste
        ../../bin/paster create -t minitage.instances.env $minibuild
    fi
fi
if [[ -e $envfile ]];then    
    source $envfile
fi
xmlreports="/opt/minitage/django/bv.server-prod/parts/bvserver.test/testreports"
tested_packages="
bv.server"
# vim:set et sts=4 ts=4 tw=80:
