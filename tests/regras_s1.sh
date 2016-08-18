#!/bin/sh
dpctl add-flow tcp:127.0.0.1:6634 in_port=2,idle_timeout=0,dl_dst=00:00:00:00:00:01,actions=output:1
dpctl add-flow tcp:127.0.0.1:6634 in_port=3,idle_timeout=0,dl_dst=00:00:00:00:00:01,actions=output:1
dpctl add-flow tcp:127.0.0.1:6634 in_port=4,idle_timeout=0,dl_dst=00:00:00:00:00:01,actions=output:1
dpctl add-flow tcp:127.0.0.1:6634 in_port=1,idle_timeout=0,dl_dst=00:00:00:02:00:01,actions=output:3
