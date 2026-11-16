#!/bin/bash
set -euo pipefail
umask 077
unset ACTIONS_RUNNER_PRINT_LOG_TO_STDOUT
export RUNNER_MANUALLY_TRAP_SIG=1
mkdir -p /state/home /work
if [ ! -x /state/runner/run.sh ]; then
  cp -a /opt/runner-dist /state/runner
fi
cd /state/runner
if [ "${1:-}" = --register ]; then
  read -r ACTIONS_RUNNER_INPUT_TOKEN
  export ACTIONS_RUNNER_INPUT_TOKEN
  exec ./config.sh --unattended --url https://github.com/ThomasHFWright/aur-anarlog-bin \
    --name "$RUNNER_NAME" --labels "$RUNNER_LABEL" --work /work
fi
test -f .runner
# The unprivileged package builder must traverse runner-created work directories.
if [ "$RUNNER_LABEL" = anarlog-build ]; then
  umask 022
fi
exec ./run.sh
