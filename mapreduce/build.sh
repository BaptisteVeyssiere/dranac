#!/bin/bash

dir=`dirname $0`

clean_dependencies() {
  for dep in `cat $dir/lib/todelete.txt`
  do
      rm -rf $dir/lib/$dep $dir/lib/$dep*-info 2>/dev/null
  done
}

build_project() {
  if [ ! `which pip` ]
  then
    echo "pip not found. pip is required to install dependencies."
    exit 1;
  fi
  clean_dependencies

  pip install --exists-action=s -r $dir/lib/requirements.txt -t $dir/lib/ --upgrade || exit 1
}

case "$1" in
  build_project)
    build_project
    ;;
  clean_dependencies)
    clean_dependencies
    ;;
  *)
    echo $"Usage: $0 {build_project|clean_dependencies}"
    exit 1
esac
