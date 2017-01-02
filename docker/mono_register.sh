#!/bin/bash
docker run --name mono -d -t -v `pwd`/cs:/cs \
           --workdir=/cs/ \
           nfox/mono:latest /bin/cat
