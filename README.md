map_unexplore
=============

Scripts for Minetest game map v25 format.

mt_block_parser.py - Can do partial or full parsing of map block. Can reassemble("Compile") block back to binary data.


remap.py - Decrease minetest map size and saves it as backup(most likely even online).

domap.py - Creates simple image, to show where player hawe built something.

clrmap.py - Clears all objects from map and saves it as backup.

mt_block_parser.py - Can be used to read map block data from your code.

recover.py - Copy only helthy map blocks.

mirrormap.py - Creates mirrored version of map.

Now can be used like "script.py <source.sqlite> <target.sqlite>" (or "<pythonpath>\python.exe script.py <source.sqlite> <target.sqlite>" on Windows)
