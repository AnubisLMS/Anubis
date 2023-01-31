#!/bin/bash -x

# Add nodes
nodes=(
)

POOL=$(echo "${nodes[0]}" | awk -F- '{print $1"-"$2}')
NODE_JSON="$(doctl --context anubis kubernetes cluster node-pool get anubis ${POOL} -o json)"


for node in ${nodes[@]}; do
    if kubectl describe node ${node} | grep -P ' theia-' &> /dev/null; then
        echo "ides on ${node}"
        continue
    fi

    NODE_ID=$(doctl --context anubis kubernetes cluster node-pool get anubis ${POOL} -o json | jq ".[0].nodes[] | select(.name == \"${node}\") | .id" -r)

    echo "deleting node=${node}"
    doctl --context anubis kubernetes cluster node-pool delete-node anubis ${POOL} ${NODE_ID} -f
done
