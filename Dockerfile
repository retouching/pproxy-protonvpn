FROM ubuntu:22.04

ENV PVPN_USERNAME= \
    PVPN_PASSWORD= \
    PVPN_TIER= \
    PVPN_SERVER= \
    PVPN_COUNTRY= \
    PPROXY_LISTEN=

RUN apt update && apt install python3 python3-pip coreutils openvpn procps runit -y && pip3 install protonvpn-cli pproxy && mkdir -p /root/.pvpn-cli
COPY pvpn-cli.cfg.clean /root/.pvpn-cli/
COPY run.py /

WORKDIR /

ENTRYPOINT ["python3", "-u", "run.py"]