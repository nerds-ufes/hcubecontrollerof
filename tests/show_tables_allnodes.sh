#!/bin/bash
# Script para listar todos as regras instaladas em todas as tabelas
# Rafael S. Guimaraes e Dione Sousa Albuquerque
SEQ=6634

OVS_OFCTL=$(which ovs-ofctl)

for i in `seq 1 8`;
do
    printf "\033[40;34;01m ##########  DPID $i ###   \033[m\n"
    $OVS_OFCTL -O Openflow13 dump-flows tcp:127.0.0.1:$SEQ | grep --color=auto "dl_dst=00:00:00"
    ((SEQ=SEQ+1))
done