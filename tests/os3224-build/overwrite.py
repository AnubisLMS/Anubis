#!/usr/bin/python3

# overwrite the README.md file with lorem ipsum


import lorem
import random

with open('README.md', 'w') as f:
<<<<<<< HEAD
    sentences = [lorem.sentence() for _ in range(5)]
=======
    sentences = [lorem.get_sentence() for _ in range(5)]
>>>>>>> 14d9e5e2612b76ef032d1cb83acb6600d1693e17
    for _ in range(30):
        f.write(random.choice(sentences) + '\n')
    f.close()
