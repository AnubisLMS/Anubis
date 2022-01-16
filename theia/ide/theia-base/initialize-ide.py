#!/usr/bin/env python3

import os
import json
import shutil
import base64

autosave = os.environ.get('AUTOSAVE', None)
incluster = os.environ.get('INCLUSTER', None)
course_context = os.environ.get('COURSE_CONTEXT', None)

if incluster is not None:
    os.makedirs('/home/anubis/.anubis/', exist_ok=True)
    json.dump({
        "incluster": base64.b64decode(incluster.encode()).decode(),
        'course_context': course_context,
    }, open('/home/anubis/.anubis/config.json', 'w'))
else:
    print('CANNOT SEE INCLUSTER ENV')


if autosave is not None:
    with open('/tmp/AUTOSAVE', 'w') as f:
        f.write(autosave)
else:
    print('CANNOT SEE AUTOSAVE ENV')


for item in os.listdir('/etc/anubis/skel'):
    if not os.path.exists(os.path.join('/home/anubis', item)):
        if os.path.isdir(os.path.join('/home/anubis', item)):
            shutil.copytree(
                os.path.join('/etc/anubis/skel', item),
                os.path.join('/home/anubis', item),
            )
        else:
            shutil.copy(
                os.path.join('/etc/anubis/skel', item),
                os.path.join('/home/anubis', item),
            )


for item in os.listdir('/etc/anubis/init.d'):
    if item.endswith('.sh'):
        os.system(f'bash /etc/anubis/init.d/{item}')
    if item.endswith('.py'):
        os.system(f'python3 /etc/anubis/init.d/{item}')

