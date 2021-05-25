#!/bin/sh

cd $(dirname $(realpath $0))

if [ ! -d node_modules ]; then
    yarn add @mermaid-js/mermaid-cli
fi

if [ ! -d ../img ]; then
    mkdir ../img
fi

for mmdf in $(find -name '*.mmd'); do
    if [ ! -f ../img/${mmdf}.png ] && [ ! -f ../img/${mmdf}.svg ]; then
        echo "mermaid rendering ${mmdf}"
        node_modules/.bin/mmdc -i ${mmdf} -o ../img/${mmdf}.png -b transparent -t forest
        node_modules/.bin/mmdc -i ${mmdf} -o ../img/${mmdf}.svg -b transparent -t forest
    else
        echo "mermaid skipping ${mmdf}"
    fi
done
