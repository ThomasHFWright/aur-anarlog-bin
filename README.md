# anarlog-bin

Community AUR package maintained by [Snoopey](https://aur.archlinux.org/account/Snoopey), based on [Anarlog's upstream recipe](https://github.com/fastrepl/anarlog/tree/main/packaging/aur/anarlog-bin).

Install with an AUR helper, for example `paru -S anarlog-bin`.

## Automatic updates

GitHub Actions checks upstream every six hours, at minute 47 UTC. Metadata updates open a PR, build the x86_64 package in an Arch container, and verify the ARM64 download checksum. Passing updates merge automatically, rebuild on main, and publish PKGBUILD and .SRCINFO to AUR. The publication key is only available in the separate publish job, never during the package build.

Only version, release number, and checksum changes are automatic. Changed upstream build instructions, downgrades, changed checksums without a version bump, and failed checks require manual review. Actions notifications and the repository's Actions tab report failures. ARM64 runtime behavior is not tested.

This follows the workflow used by [aur-omnigent-desktop](https://github.com/ThomasHFWright/aur-omnigent-desktop). The repository secret `AUR_SSH_PRIVATE_KEY` holds the existing AUR publisher key; `.github/aur-known-hosts` pins AUR's SSH host key.

To check immediately, run the **Propose stable release update** workflow manually. To pause automatic checks, disable that workflow in GitHub Actions. GitHub may disable scheduled workflows in public repositories after 60 days without repository activity; re-enable the workflow if this happens.

This updates the AUR entry. Installed copies update through the user's normal AUR helper or package manager.
