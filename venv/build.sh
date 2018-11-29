#!/bin/bash

dir=`dirname $0`
demo_dir=`pwd`

build_demo () {
  fetch_dependencies
  [ ! -d "$demo_dir/demo/mapreduce" ] && ln -s "$demo_dir/src/mapreduce" "$demo_dir/demo"
}

run_demo () {
  build_demo
  dev_appserver.py "$dir/demo"
}

fetch_dependencies() {
  if [ ! `which pip` ]
  then
    echo "pip not found. pip is required to install dependencies."
    exit 1;
  fi
  # Work arround https://github.com/pypa/pip/issues/1356
  for dep in `cat $dir/src/todelete.txt`
  do
      rm -r $dir/src/$dep $dir/demo/$dep  $dir/src/$dep*-info $dir/demo/$dep*-info 2>/dev/null
  done

  pip install --exists-action=s -r $dir/src/requirements.txt -t $dir/src/ --upgrade || exit 1
  pip install --exists-action=s -r $dir/src/requirements.txt -t $dir/demo/ --upgrade || exit 1
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
