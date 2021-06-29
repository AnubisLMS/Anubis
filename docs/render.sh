#!/bin/sh

# Switch to the directory that this script is in (docs)
cd $(realpath $(dirname $0))

echo 'Rendering README.md to anubis.pdf'
set -ex

cd mermaid
if ! [ -d node_modules ]; then
    yarn
fi
./render.sh

cd ../
exec pandoc README.md -s -o anubis.pdf -f markdown-implicit_figures
