We welcome contributions from the community. Please read the following
guidelines carefully to maximize the chances of your PR being merged.

## Submitting a PR

* Fork the repository to your own account
* Create your PR
* Your PR description should have details on what the PR does. If it fixes an
  existing issue it should end with "Fixes #XXX".
* If your PR does not apply to the current or all versions of Kubernetes,
  or the master branch of Wardroom, list which versions of Kubernetes the
  PR applies to, and make sure your PR is into the branch representing the
  latest version of Kubernetes your PR applies to.
* Once you submit a PR, *please do not rebase it*. It's much easier to review if
  subsequent commits are new commits and/or merges. We squash rebase the final
  merged commit so the number of commits you have in the PR don't matter.
* We expect that once a PR is opened, it will be actively worked on until it is
  merged or closed. We reserve the right to close PRs that are not making
  progress. This is generally defined as no changes for 7 days. Obviously PRs
  that are closed due to lack of activity can be reopened later. Closing stale
  PRs helps us to keep on top of all of the work currently in flight.

## PR review policy for maintainers

* Typically we try to turn around reviews within one business day.
* It is generally expected that a maintainer should review every PR.
* It is also generally expected that a "domain expert" for the code the PR
  touches should review the PR. This person does not necessarily need to have
  commit access.
* Anyone is welcome to review any PR that they want, whether they are a
  maintainer or not.
* Please **clean up the title and body** before merging. By default, GitHub
  fills the squash merge title with the original title, and the commit body with
  every individual commit from the PR. The maintainer doing the merge should
  make sure the title follows the guidelines above and should overwrite the body
  with the original extended description from the PR (cleaning it up if
  necessary) while preserving the PR author's final DCO sign-off.

## DCO Sign off

All authors to the project retain copyright to their work. However, to ensure
that they are only submitting work that they have rights to, we are requiring
everyone to acknowldge this by signing their work.

Any copyright notices in this repos should specify the authors as "The
project authors".

To sign your work, just add a line like this at the end of your commit message:

```
Signed-off-by: Joe Beda <joe@heptio.com>
```

This can easily be done with the `--signoff` option to `git commit`.

By doing this you state that you can certify the following (from
https://developercertificate.org/):

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
1 Letterman Drive
Suite D4700
San Francisco, CA, 94129

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```
