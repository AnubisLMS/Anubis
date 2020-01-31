#!/usr/bin/python3

# overwrite the README.md file with lorem ipsum


import lorem
import random

with open('README.md', 'w') as f:
    sentences = [lorem.get_sentence() for _ in range(5)]
    for _ in range(30):
        f.write(random.choice(sentences) + '\n')
    f.close()
