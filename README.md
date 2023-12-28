This is a set of programs for solving the Synacor Challenge. You can
find an archived copy of the challenge here:

https://github.com/Aneurysm9/vm_challenge

I recommend trying the challenge without reading any further or
looking at my code if you want to avoid spoilers.

* vm.py
  - the virtual machine that runs the challenge.bin file
* coins.py
  - program to solve the coins puzzle
* orb.py
  - program to solve the orb puzzle
* teleport.py
  - program to solve the teleporter puzzle

The VM has system commands that start with "!". Type "!help" for a
list of these commands.

If you're going to use the "!tp" command to search for the teleporter
code, I recommend using pypy3. Running the teleport.py script with
pypy3 should be faster.
