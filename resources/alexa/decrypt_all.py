#!/usr/bin/env python2

import sys
sys.path.append("../../lib/ubuntu64")
import decrypt

if len(sys.argv) != 2:
    print('Usage: decrypt_all.py model_file')
    exit(1)

f_in = open(sys.argv[1])
data = f_in.read()
decode = decrypt.DecryptString(data)
f_in.close()

f_out = open(sys.argv[1]+'.dec', 'w')
f_out.write(decode)
f_out.close()

