# Anubis CLI

## Install
To install the anubis cli, clone then navigate to the Anubis repo in the terminal.
You can then pip install the cli with either `make acli` or `sudo pip3 install ./acli`. 
Verify that the cli was installed by running `anubis -h`.


## Usage 
There are several functions built into the cli so you can manage some functions of the 
Anubis cluster on your own. You will be prompted for a username password when using the cli
for the first time. The credentials that you use will be saved locally, so you will not be
prompted after the first time.


### Logout of cli
To delete your saved cli credentials, run `anubis logout`.


### Dangling submissions
Anubis needs to be able to match a github username to a netid. If and when a job request comes in
for a github username that has no matching netid, a so called "dangling" submission will be created.
Basically the submission is recorded, but it is not processed by the cluster. Uploading the missing 
student data will fix dangling submissions.


### Student data
To upload student data to anubis, use the student command. First, make a json file that has this shape:

```
[
  {
    "netid": "jmc1283",
    "first_name": "John",
    "last_name": "Cunniff",
    "github_username": "jmc1283"
  }
]
```

You can add as many student to this array as you need. When you push this data to Anubis, it will
also attempt to fix dangling submissions.

```bash
anubis student <filename>
```

### Restart / re-enqueue a submission
To re-enqueue a submission, use the restart command. This command takes a netid, and optinally a commit hash.
Without the commit option, the api will just re-enqueue the most recent submission for that netid.

```bash
anubis restart jmc1283
anubis restart jmc1283 2bc7f8d636365402e2d6cc2556ce814c4fcd1489
```

### Submission Stats
To get the statistics for an assignment, you can use the stats command. Provide this command with an
assignment name, and it will run though all processed submissions, getting the best submission for a netid.
The best submission is determined to be the most recent submission with the most tests passing. 

To get the statistics for say os3224-assignment-2,

```bash
anubis stats os3224-assignment-2
```

You can also get statstics for a single netid with
```bash
anubis stats os3224-assignment-2 jmc1283
```

### List processing submission
Use the ls command to verify if a submission is actually being enqueued. You may need to be speady with running
this command. It will only show submissions that are currently in a processing state. Jobs will be processed very 
quickly, so your window for seeing it in a processing state may only be a few seconds.

```bash
anubis ls
```


