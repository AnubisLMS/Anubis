import requests
import json

r = requests.post(
    'http://localhost:5000/private/assignment/5/question/sync',
    json={
        'questions': [
            {
                'question': 'Who',
                'solution': 'solution 1',
                'sequence': 1,
            },
            {
                'question': 'What',
                'solution': 'solution 2',
                'sequence': 1,
            },
            {
                'question': 'Where',
                'solution': 'solution 3',
                'sequence': 2,
            },
        ]
    },
    headers={'Content-Type': 'application/json'}
)
print(r, r.status_code)
print(json.dumps(r.json(), indent=2))
print()


r = requests.get('http://localhost:5000/private/assignment/5/questions/assign')
print(r, r.status_code)
print(json.dumps(r.json(), indent=2))
print()
