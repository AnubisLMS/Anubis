#!/usr/bin/python3

"""
This program will take the csv form of the nyuclasses quiz and
convert it to the json form for acli to be able to ingest.
"""

import json
import csv

filename= './github IDs - Responses.csv'

students=[]
with open(filename, newline='') as csvfile:
    reader=csv.DictReader(csvfile)
    for row in reader:
        students.append({
            'netid': row['User Name'],
            'first_name': row['First Name'],
            'last_name': row['Last Name'],
            'email': row['Part 1, Question 1, Response'],
            'github_username': row['Part 1, Question 2, Response'],
        })

students.pop(0)

print(json.dumps(students, indent=2))
