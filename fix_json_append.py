import json
import sys

if len(sys.argv) != 2:
    raise ValueError('Ples provide file')

outfile_name = 'FIXED_json.json'

with open(sys.argv[1], 'r') as infile:
    data = json.loads(infile.read())
    for prof in data:
        for p_tup in data[prof]:
            if len(p_tup) == 3: # no need for fix
                continue
            elif len(p_tup) > 3: # length should be 3
                p_tup[2] = p_tup[len(p_tup) - 1] # add doc 2nd index
                del p_tup[3:]
infile.close()

# save file
with open(outfile_name, 'w+') as outfile:
    json.dump(data, outfile)



