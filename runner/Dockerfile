FROM local/github-actions-runner:2.338.2 AS runner
FROM archlinux:base-devel
RUN pacman -Syu --noconfirm --needed git python github-cli icu krb5 zlib openssl lttng-ust \
    && useradd --create-home builder
COPY --from=runner /opt/runner-dist /opt/runner-dist
COPY --from=runner /usr/local/bin/clean-work.py /usr/local/bin/clean-work.sh /usr/local/bin/
COPY start.sh /usr/local/bin/start.sh
ENV HOME=/state/home RUNNER_ALLOW_RUNASROOT=1 \
    ACTIONS_RUNNER_HOOK_JOB_COMPLETED=/usr/local/bin/clean-work.sh
WORKDIR /state
ENTRYPOINT ["/bin/bash", "/usr/local/bin/start.sh"]
