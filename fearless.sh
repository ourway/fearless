#!/bin/bash
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
          DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
            SOURCE="$(readlink "$SOURCE")"
              [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
export FEARLESS_ROOT="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
cd $FEARLESS_ROOT;
source pyenv/bin/activate;
export PS1="Fearless: "
