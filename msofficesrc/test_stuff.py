



import re

mystring = "abcdef+gh\i`!&/()=herp*?th<ede>rp..-"

print(re.sub(r"[/:*?\"<>|]+", '-', mystring))
