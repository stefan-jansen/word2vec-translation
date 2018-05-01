#!/usr/bin/env bash
pushd . &> /dev/null
cd /tmp
git clone --depth=1 https://github.com/tmikolov/word2vec
cd word2vec
sed -i -e 's/malloc.h/stdlib.h/g' *.c
make
rm *.c* *.txt makefile LICENSE
cp * /usr/local/bin
popd &> /dev/null