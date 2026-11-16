# anarlog-bin

Community AUR package maintained by [Snoopey](https://aur.archlinux.org/account/Snoopey), based on [Anarlog's upstream recipe](https://github.com/fastrepl/anarlog/tree/main/packaging/aur/anarlog-bin).

Install with an AUR helper, for example `paru -S anarlog-bin`.

## Automatic updates

GitHub Actions schedules checks every six hours, at minute 47 UTC, on dedicated runners on `validator.host`. Metadata updates open a PR, build the x86_64 package in the local Arch runner container, and verify the ARM64 download checksum. Passing updates merge automatically, rebuild on main, and publish PKGBUILD and .SRCINFO to AUR. The publication key is only available in the separate publish job, never during the package build.

Only version, release number, and checksum changes are automatic. Changed upstream build instructions, downgrades, changed checksums without a version bump, and failed checks require manual review. Actions notifications and the repository's Actions tab report failures. ARM64 runtime behavior is not tested.

This retains the validated update and publication flow used by [aur-omnigent-desktop](https://github.com/ThomasHFWright/aur-omnigent-desktop), with all jobs running on Validator instead of GitHub-hosted machines. GitHub API metadata requests use the short-lived job token to avoid anonymous rate limits; download requests do not receive that token. The repository secret `AUR_SSH_PRIVATE_KEY` holds the existing AUR publisher key; `.github/aur-known-hosts` pins AUR's SSH host key.

To check immediately, run the **Propose stable release update** workflow manually. To pause automatic checks, disable that workflow in GitHub Actions. GitHub may disable scheduled workflows in public repositories after 60 days without repository activity; re-enable the workflow if this happens.

This updates the AUR entry. Installed copies update through the user's normal AUR helper or package manager.

## Validator runners

Deployment files are in `runner/`, installed at
`/home/tom/.local/share/anarlog-aur-runner` on Validator. The builder image reuses
the official runner distribution from the existing
`local/github-actions-runner:2.338.2` image and runs in Arch Linux. The publisher
uses that existing Ubuntu image. Both keep native runner updates in dedicated
state volumes and restart automatically with Docker. Neither has a Docker
socket or host credentials mounted. These runners accept only this repository's
trusted main/update-branch workflows; do not enable arbitrary pull-request jobs.

`validator-anarlog-build` handles update discovery and unprivileged package
builds. `validator-anarlog-publish` handles status reporting, merge, and AUR
publication, with separate state/work volumes. The AUR key remains a GitHub
Actions secret, supplied only during publication. There is no hosted fallback:
checks queue while Validator is unavailable.

Initial setup: build with `docker compose build build`. Register each service
once using `docker compose run --rm -T SERVICE --register`, supplying a fresh
GitHub repository runner registration token through stdin. Run
`docker compose up -d` afterward. Registration tokens are not saved in Compose.
Check status with `docker compose ps`, `docker compose logs --tail=50`, and the
repository's Actions runner settings. Before changing a runner, wait until it
is idle. Lost state volumes require fresh registration; work volumes contain
only disposable job/build files. Stop the stack with `docker compose stop`.

After deploying a change, manually run **Propose stable release update** and
verify build, merge, publication, and the AUR package version. Self-checks:
`python .github/scripts/update-release.py --self-test`,
`bash -n runner/start.sh`, and `docker compose -f runner/compose.yaml config --quiet`.
