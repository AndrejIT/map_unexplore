#!/usr/bin/env python
#Licence LGPL v2.1

#https://github.com/minetest/minetest/blob/944ffe9e532a3b2be686ef28c33313148760b1c9/doc/mapformat.txt
#http://www.tutorialspoint.com/sqlite/sqlite_bitwise_operators.htm
#http://stackoverflow.com/questions/1294619/does-sqlite-support-any-kind-of-ifcondition-statement-in-a-select


import sqlite3
import mt_block_parser

import re

from PIL import Image, ImageDraw, ImageFont, ImageColor

#It is possible to get X, Y, Z directly by SQLite!
#for row in sourcecursor.execute(" SELECT "+
#                                " CASE WHEN `X` < 2048 THEN `X` ELSE `X` - 4096 END AS X, "+
#                                " CASE WHEN `Y` < 2048 THEN `Y` ELSE `Y` - 4096 END AS Y, "+
#                                " CASE WHEN `Z` < 2048 THEN `Z` ELSE `Z` - 4096 END AS Z "+
#                                " FROM ("+"SELECT "+
#                                    " (`pos`) & 4095 AS X, "+
#                                    " ((`pos`) & 16773120)>>12 AS Y, "+
#                                    " ((`pos`) & 68702699520)>>24 AS Z "+
#                                    " FROM `blocks`"+
#                                ")"):

source = r'<Put your path to world folder here>/map.sqlite'
target_image = r'<Put your path to world folder here>/map.png'

#use compiled regular expression to filter blocks by block content. it is faster that checking "in array".
useful_block_evidence = re.compile(
"default:cobble|"+
"protector:protect|default:chest_locked|doors:door_steel|"+
"default:chest|default:torch|default:stonebrick|default:glass|default:obsidian_glass|"+
"default:ladder|default:rail|default:fence_wood|"+
"bones:bones"
)

sourceconn = sqlite3.connect(source)
sourcecursorXZ = sourceconn.cursor()
sourcecursor = sourceconn.cursor()

#X and Z min and max to know image size
for rowMinMax in sourcecursorXZ.execute(" SELECT "+
                                " MIN( CASE WHEN `X` < 2048 THEN `X` ELSE `X` - 4096 END ) AS minX, "+
                                " MIN( CASE WHEN `Z` < 2048 THEN `Z` ELSE `Z` - 4096 END ) AS minZ, "+
                                " MAX( CASE WHEN `X` < 2048 THEN `X` ELSE `X` - 4096 END ) AS maxX, "+
                                " MAX( CASE WHEN `Z` < 2048 THEN `Z` ELSE `Z` - 4096 END ) AS maxZ "+
                                " FROM ("+"SELECT "+
                                    " (`pos`) & 4095 AS X, "+
                                    " ((`pos`) & 68702699520)>>24 AS Z "+
                                    " FROM `blocks`"+
                                ")"):
    minX = rowMinMax[0]
    minZ = rowMinMax[1]
    maxX = rowMinMax[2]
    maxZ = rowMinMax[3]
    width = maxZ - minZ
    height = maxX - minX

image = Image.new("RGB", (width, height), (0,0,0,0))
draw = ImageDraw.Draw(image)
impixel = image.load()

#assuming that map is moustly flat limit Y coordinate
for row in sourcecursor.execute(" SELECT "+
                                " CASE WHEN `X` < 2048 THEN `X` ELSE `X` - 4096 END AS X, "+
                                " CASE WHEN `Y` < 2048 THEN `Y` ELSE `Y` - 4096 END AS Y, "+
                                " CASE WHEN `Z` < 2048 THEN `Z` ELSE `Z` - 4096 END AS Z, "+
                                " `pos`, "+
                                " `data` "+
                                " FROM ("+"SELECT "+
                                    " `pos`, "+
                                    " (`pos`) & 4095 AS X, "+
                                    " ((`pos`) & 16773120)>>12 AS Y, "+
                                    " ((`pos`) & 68702699520)>>24 AS Z, "+
                                    " `data` "+
                                    " FROM `blocks`"+
                                ")"+
                                " WHERE Y>-5 AND Y<5; "):
    try:
        block = mt_block_parser.MtBlockParser(row[4])
        if useful_block_evidence.search(block.nameIdMappingsRead)!=None:
            impixel[ row[0] - minX, height - row[2] + minZ ] = (255, 255, 200)
    except:
        print "Block parse error:", row[0], row[1], row[2]

sourceconn.close()

draw.ellipse((-minX - 5, height + minZ - 5, -minX + 5, height + minZ + 5), outline=(255, 0, 0)) #map center
image.save(target_image)
