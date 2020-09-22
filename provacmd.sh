#!/bin/sh

    if "sh -c lsof -n -i4TCP:8222 | grep LISTEN"; then
        echo "Worked"
    else
        return "${?}"
fi
