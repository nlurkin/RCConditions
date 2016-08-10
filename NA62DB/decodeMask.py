#!/usr/bin/env python

import math 

mask = "0x7fdf7fff"
mask = int(mask, 0)
dc = mask >> 16
prim = mask & 0xffff

inv_dc = ~dc & 0xffff
inv_prim = ~prim & 0xffff
pos_bits = prim & inv_dc
neg_bits = inv_prim & inv_dc
print "dc {0:>#6x}  {0:#018b}".format(dc)
print "pr {0:>#6x}  {0:#018b}".format(prim)
print "ip {0:>#6x}  {0:#018b}".format(inv_prim)
print "id {0:>#6x}  {0:#018b}".format(inv_dc)
print "+  {0:>#6x}  {0:#018b}".format(pos_bits)
print "-  {0:>#6x}  {0:#018b}".format(neg_bits)

nbitList = []
while neg_bits!=0:
    bitval = int(math.log(neg_bits, 2))
    if bitval!=15:
        nbitList.append(str(bitval)) 
    neg_bits = neg_bits - (1<<bitval)

print "neg bits: " + ",".join(nbitList)

pbitList = []
while pos_bits!=0:
    bitval = int(math.log(pos_bits, 2))
    if bitval!=14 or len(nbitList)==0:
        pbitList.append(str(bitval)) 
    pos_bits = pos_bits - (1<<bitval)

print "pos bits: " + ",".join(pbitList)

