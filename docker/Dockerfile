FROM mono:latest
MAINTAINER Nickolas Fox <tarvitz@blacklibrary.ru>
RUN set -x \
    && groupadd -g 1000 user \
    && useradd -m -g user -u 1000 user
USER user

