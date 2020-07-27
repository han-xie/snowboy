#!/usr/bin/env bash

current_path=`pwd`
current_dir=`basename "$current_path"`
obj_dir="obj_files"

if [ "ubuntu64" != "$current_dir" ]; then
  echo "You should run this script in ubuntu64/ directory!!"
  exit 1
fi

mkdir $obj_dir
cd $obj_dir
ar x $current_path/libsnowboy-detect.a
cd $current_path

if ! which swig > /dev/null; then
  echo "$0: swig is not installed, you can install with"
  echo "    sudo apt install swig (in ubuntu)"
  exit 1
fi

swig -python -c++ token.i
g++ -fPIC -shared decrypt.cc token_wrap.cxx $obj_dir/snowboy-io.o $obj_dir/snowboy-debug.o $obj_dir/snowboy-utils.o -o _token.so -I/usr/include/python2.7 -D_GLIBCXX_USE_CXX11_ABI=0

rm -rf $obj_dir

if [ "<UniversalModel>" == `$current_path/decrypt_token.py` ]; then
  echo "test passed"
else
  echo "test NOT passed"
fi

