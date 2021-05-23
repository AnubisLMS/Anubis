#!/bin/sh

echo 'Rendering design.md to design.pdf'

set -ex

cd mermaid
if ! [ -d node_modules ]; then
    yarn
fi
./render.sh

cd ../../
exec pandoc README.md -s -o docs/design.pdf -f markdown-implicit_figures
