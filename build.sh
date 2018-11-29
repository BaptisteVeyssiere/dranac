#!/bin/bash

dir=`dirname $0`
demo_dir=`pwd`

build_demo () {
  fetch_dependencies
}

run_demo () {
  build_demo
  dev_appserver.py "$dir"
}

fetch_dependencies() {
  if [ ! `which pip` ]
  then
    echo "pip not found. pip is required to install dependencies."
    exit 1;
  fi
  # Work arround https://github.com/pypa/pip/issues/1356
  for dep in `cat $dir/lib/todelete.txt`
  do
      rm -r $dir/lib/$dep $dir/$dep  $dir/lib/$dep*-info $dir/$dep*-info 2>/dev/null
  done

  pip install --exists-action=s -r $dir/lib/requirements.txt -t $dir/lib/ --upgrade || exit 1
}

case "$1" in
  build_demo)
    build_demo
    ;;
  run_demo)
    run_demo
    ;;
  *)
    echo $"Usage: $0 {build_demo|run_demo}"
    exit 1
esac
