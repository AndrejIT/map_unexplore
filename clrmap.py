#!/usr/bin/env python
#Licence LGPL v2.1

#Copy all blocks, but remove from them all objects.

import sqlite3
import mt_block_parser

import struct
import zlib

source = r'<Put your path to world folder here>/map.sqlite.backup'
target = r'<Put your path to world folder here>/map.sqlite.clear'

sourceconn = sqlite3.connect(source)
targetconn = sqlite3.connect(target)
sourcecursor = sourceconn.cursor()
targetcursor = targetconn.cursor()
targetcursor.execute("CREATE TABLE IF NOT EXISTS `blocks` (`pos` INT NOT NULL PRIMARY KEY, `data` BLOB);")

for row in sourcecursor.execute("SELECT `pos`, `data` "+" FROM `blocks`;"):
    block = mt_block_parser.MtBlockParser(row[1])
    if block.static_object_count == 0:
        targetcursor.execute("INSERT OR IGNORE INTO `blocks` VALUES (?, ?);", (row[0], row[1]))
    else:
        #combine block back to string, but leave objects out
        cleared_block = ""
        cleared_block+= struct.pack('B', block.version)
        cleared_block+= struct.pack('B', block.flags)
        cleared_block+= struct.pack('B', block.content_width)
        cleared_block+= struct.pack('B', block.params_width)
        cleared_block+= zlib.compress(block.nodeDataRead)
        cleared_block+= zlib.compress(block.nodeMetadataRead)
        cleared_block+= struct.pack('B', block.static_object_version)
        cleared_block+= struct.pack('>H', 0) #Set static_object_count to zero
        #cleared_block+= block.objectsRead - Don't copy objects
        cleared_block+= struct.pack('>I', block.timestamp)
        cleared_block+= struct.pack('B', block.name_id_mapping_version)
        cleared_block+= struct.pack('>H', block.num_name_id_mappings)
        cleared_block+= block.nameIdMappingsRead
        cleared_block+= struct.pack('B', block.length_of_timer)
        cleared_block+= struct.pack('>H', block.num_of_timers)
        cleared_block+= block.timersRead
        targetcursor.execute("INSERT OR IGNORE INTO `blocks` VALUES (?, ?);", (row[0], sqlite3.Binary(cleared_block)))
            
targetconn.commit()

sourceconn.close()
targetconn.close()
