#!/usr/bin/python3

# overwrite the README.md file with lorem ipsum


import lorem
import random

with open('short', 'w') as f:
    sentences = [lorem.sentence() for _ in range(5)]
    for _ in range(30):
        f.write(random.choice(sentences) + '\n')
    f.close()


with open('long', 'w') as f:
    sentences = [lorem.paragraph() for _ in range(5)]
    for _ in range(30):
        f.write(random.choice(sentences) + '\n')
    f.close()
