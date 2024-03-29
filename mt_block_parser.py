#!/usr/bin/env python

#Licence LGPL v2.1
#Created for version 25. Updated to support version 28.
#https://github.com/minetest/minetest/blob/944ffe9e532a3b2be686ef28c33313148760b1c9/doc/mapformat.txt
#https://github.com/minetest/minetest/blob/master/doc/world_format.txt

import sys
import struct
import zlib
import re

class MtBlockParser:
    'Allows to read different data from Minetest map v.25 block'
    length = None

    version = 25
    flags = None
    content_width = 2
    params_width = 2

    nodeDataRead = bytearray()
    arrayParam0 = None
    arrayParam1 = None
    arrayParam2 = None

    nodeMetadataRead = bytearray()
    metadata_version = 2    # 2 since map version 28
    metadata_count = None
    arrayMetadataRead = None
    arrayMetadataReadPrivate = None
    arrayMetadataReadInventory = None

    static_object_version = 0
    static_object_count = None
    objectsRead = bytearray()
    #TODO

    timestamp = None

    name_id_mapping_version = 0
    num_name_id_mappings = None
    nameIdMappingsRead = bytearray()
    nameIdMappings = None

    length_of_timer = 10
    num_of_timers = None
    timersRead = bytearray()
    arrayTimerTimeout = None
    arrayTimerElapsed = None

    def __init__(self, blockBlob):
        self.nodeDataRead = bytearray()
        self.nodeMetadataRead = bytearray()
        self.objectsRead = bytearray()
        self.nameIdMappingsRead = bytearray()
    
        self.arrayParam0 = {}
        self.arrayParam1 = {}
        self.arrayParam2 = {}
        self.arrayMetadataRead = {}
        self.arrayMetadataReadPrivate = {}
        self.arrayMetadataReadInventory = {}
        self.nameIdMappings = {}
        self.arrayTimerTimeout = {}
        self.arrayTimerElapsed = {}

        if blockBlob:
            self.length = len(blockBlob)

            cursor = 0
            if self.version > struct.unpack('B', blockBlob[cursor:cursor + 1])[0]:
                print("Old version not supported!")
            if 27 <= struct.unpack('B', blockBlob[cursor:cursor + 1])[0]:
                #print("Warning for new version!")
                cursor+= 1
                self.flags = struct.unpack('B', blockBlob[cursor:cursor + 1])[0]
                cursor+= 1
                #Skipping two bytes from 27. version map format. Their purpose is for lightning recalculation
                #I will just ignore them for now and save map back to the older format
                cursor+= 1
                cursor+= 1
            else:
                cursor+= 1
                self.flags = struct.unpack('B', blockBlob[cursor:cursor + 1])[0]
                cursor+= 1
            if self.content_width != struct.unpack('B', blockBlob[cursor:cursor + 1])[0]:
                print("Content width not supported!", struct.unpack('B', blockBlob[cursor:cursor + 1])[0])
            cursor+= 1
            if self.params_width != struct.unpack('B', blockBlob[cursor:cursor + 1])[0]:
                print("Params width not supported!", struct.unpack('B', blockBlob[cursor:cursor + 1])[0])
            cursor+= 1
            decompressor = zlib.decompressobj()
            self.nodeDataRead = decompressor.decompress( blockBlob[cursor:] )
            cursor = self.length - len(decompressor.unused_data)
            decompressor = zlib.decompressobj()
            self.nodeMetadataRead = decompressor.decompress( blockBlob[cursor:] )
            cursor = self.length - len(decompressor.unused_data)
            if self.static_object_version != struct.unpack('B', blockBlob[cursor:cursor + 1])[0]:
                print("Object version not supported!")
            cursor+=1
            self.static_object_count = struct.unpack('>H', blockBlob[cursor:cursor + 2])[0]
            self.objectsRead.extend(blockBlob[cursor:cursor + 2])
            cursor+= 2
            for i in range(0, self.static_object_count):
                self.objectsRead.extend(blockBlob[cursor:cursor + 13])
                cursor+= 13
                self.objectsRead.extend(blockBlob[cursor:cursor + 2])
                data_size = struct.unpack('>H', blockBlob[cursor:cursor + 2])[0]
                cursor+= 2
                self.objectsRead.extend(blockBlob[cursor:cursor + data_size])
                cursor+= data_size
            self.timestamp = struct.unpack('>I', blockBlob[cursor:cursor + 4])[0]
            cursor+= 4
            if self.name_id_mapping_version != struct.unpack('B', blockBlob[cursor:cursor + 1])[0]:
                print("Name-ID mapping version not supported!")
            cursor+= 1
            self.num_name_id_mappings = struct.unpack('>H', blockBlob[cursor:cursor + 2])[0]
            self.nameIdMappingsRead.extend(blockBlob[cursor:cursor + 2])
            cursor+= 2
            for i in range(0, self.num_name_id_mappings):
                self.nameIdMappingsRead.extend(blockBlob[cursor:cursor + 2])
                cursor+= 2
                self.nameIdMappingsRead.extend(blockBlob[cursor:cursor + 2])
                data_size = struct.unpack('>H', blockBlob[cursor:cursor + 2])[0]
                cursor+= 2
                self.nameIdMappingsRead.extend(blockBlob[cursor:cursor + data_size])
                cursor+= data_size
            if self.length_of_timer != struct.unpack('B', blockBlob[cursor:cursor + 1])[0]:
                print("Length of timer not supported!")
            cursor+= 1
            self.num_of_timers = struct.unpack('>H', blockBlob[cursor:cursor + 2])[0]
            self.timersRead.extend(blockBlob[cursor:cursor + 2])
            cursor+= 2
            for i in range(0, self.num_of_timers):
                self.timersRead.extend(blockBlob[cursor:cursor + 10])
                cursor+= 10
            if self.length != cursor:
                print("Parsed length is wrong!")
        #create blank block (parsed)
        else:
            self.flags = 0
            for i in range(0, 4096):
                self.arrayParam0[i] = 1
                self.arrayParam1[i] = 1
                self.arrayParam2[i] = 1
            self.metadata_count = 0
            self.static_object_count = 0
            self.objectsRead = struct.pack('>H', 0)
            self.timestamp = 1458158584
            num_name_id_mappings = 0
            self.nameIdMappingsRead = struct.pack('>H', 0)
            self.num_of_timers = 0
            self.timersRead = struct.pack('>H', 0)


    def selfCompile(self):
        blockBlob = bytearray()
        blockBlob.extend(struct.pack('B', self.version))
        blockBlob.extend(struct.pack('B', self.flags))
        blockBlob.extend(struct.pack('B', self.content_width))
        blockBlob.extend(struct.pack('B', self.params_width))
        if sys.version_info < (3, 0, 0):
            blockBlob.extend(zlib.compress(buffer(self.nodeDataRead)))
            blockBlob.extend(zlib.compress(buffer(self.nodeMetadataRead)))
        else:
            blockBlob.extend(zlib.compress(self.nodeDataRead))
            blockBlob.extend(zlib.compress(self.nodeMetadataRead))
        blockBlob.extend(struct.pack('B', self.static_object_version))
        blockBlob.extend(self.objectsRead)
        blockBlob.extend(struct.pack('>I', self.timestamp))
        blockBlob.extend(struct.pack('B', self.name_id_mapping_version))
        blockBlob.extend(self.nameIdMappingsRead)
        blockBlob.extend(struct.pack('B', self.length_of_timer))
        blockBlob.extend(self.timersRead)
        return blockBlob

    def nodeDataParse(self):
        if self.nodeDataRead == None or self.nodeDataRead == bytearray():
            print("No node data!")
            return
        if len(self.nodeDataRead) != 4096 * 4:
            print("Node data length is wrong!")
        cursor = 0
        for i in range(0, 4096):
            self.arrayParam0[i] = struct.unpack('>H', self.nodeDataRead[cursor:cursor + 2])[0]
            cursor+= 2
        for i in range(0, 4096):
            self.arrayParam1[i] = struct.unpack('B', self.nodeDataRead[cursor:cursor + 1])[0]
            cursor+= 1
        for i in range(0, 4096):
            self.arrayParam2[i] = struct.unpack('B', self.nodeDataRead[cursor:cursor + 1])[0]
            cursor+= 1

    def nodeDataCompile(self):
        self.nodeDataRead = bytearray()
        self.nodeDataRead.extend(struct.pack('>%sH' % 4096, *self.arrayParam0.values()))
        self.nodeDataRead.extend(struct.pack('B' * 4096, *self.arrayParam1.values()))
        self.nodeDataRead.extend(struct.pack('B' * 4096, *self.arrayParam2.values()))

    def nodeMetadataParse(self):
        if self.nodeMetadataRead == None or self.nodeMetadataRead == bytearray():
            print("No node metadata!")
            return
        length = len(self.nodeMetadataRead)
        if length < 4:
            self.metadata_count = 0
            return
        cursor = 0
        block_metadata_version = struct.unpack('B', self.nodeMetadataRead[cursor:cursor + 1])[0]
        if block_metadata_version > 2 or block_metadata_version < 1:
            print("Unsuported metadata version! Trying anyway!")
        cursor+= 1
        self.metadata_count = struct.unpack('>H', self.nodeMetadataRead[cursor:cursor + 2])[0]
        cursor+= 2
        if block_metadata_version == 1:
            for i in range(0, self.metadata_count):
                position = struct.unpack('>H', self.nodeMetadataRead[cursor:cursor + 2])[0]
                cursor+= 2
                num_vars = struct.unpack('>i', self.nodeMetadataRead[cursor:cursor + 4])[0]
                cursor+= 4
                self.arrayMetadataRead[position] = {}
                self.arrayMetadataReadPrivate[position] = {}
                for j in range(0, num_vars):
                    key_len = struct.unpack('>H', self.nodeMetadataRead[cursor:cursor + 2])[0]
                    if key_len == 0:
                        cursor+= 1  # some bad guy added 1 empty bit without mentioning it in map specification???
                        print("Extra empty bit in metadata! skipping!")
                        key_len = struct.unpack('>H', self.nodeMetadataRead[cursor:cursor + 2])[0]
                        cursor+= 2  # well, no point to make any better workaround until specification is corrected
                    else:
                        cursor+= 2
                    key = self.nodeMetadataRead[cursor:cursor + key_len]
                    cursor+= key_len
                    val_len = struct.unpack('>i', self.nodeMetadataRead[cursor:cursor + 4])[0]
                    cursor+= 4
                    self.arrayMetadataRead[position][key] = self.nodeMetadataRead[cursor:cursor + val_len]
                    cursor+= val_len
                    # In old version all metadata was public
                    self.arrayMetadataReadPrivate[position][key] = 0
                #just store inventory as text (bytearray!) for now
                inventory_len = 0
                inventory = self.nodeMetadataRead[cursor:].partition(b"EndInventory\n")
                inventory = inventory[0] + inventory[1]
                inventory_len = len(inventory)
                self.arrayMetadataReadInventory[position] = inventory
                cursor+= inventory_len
        elif block_metadata_version >= 2:
            for i in range(0, self.metadata_count):
                position = struct.unpack('>H', self.nodeMetadataRead[cursor:cursor + 2])[0]
                cursor+= 2
                num_vars = struct.unpack('>i', self.nodeMetadataRead[cursor:cursor + 4])[0]
                cursor+= 4
                self.arrayMetadataRead[position] = {}
                self.arrayMetadataReadPrivate[position] = {}
                for j in range(0, num_vars):
                    key_len = struct.unpack('>H', self.nodeMetadataRead[cursor:cursor + 2])[0]
                    cursor+= 2
                    key = self.nodeMetadataRead[cursor:cursor + key_len]
                    cursor+= key_len
                    val_len = struct.unpack('>i', self.nodeMetadataRead[cursor:cursor + 4])[0]
                    cursor+= 4
                    self.arrayMetadataRead[position][key] = self.nodeMetadataRead[cursor:cursor + val_len]
                    cursor+= val_len
                    self.arrayMetadataReadPrivate[position][key] = struct.unpack('B', self.nodeMetadataRead[cursor:cursor + 1])[0]
                    cursor+= 1
                #just store inventory as text (bytearray!) for now
                inventory_len = 0
                inventory = self.nodeMetadataRead[cursor:].partition(b"EndInventory\n")
                inventory = inventory[0] + inventory[1]
                inventory_len = len(inventory)
                self.arrayMetadataReadInventory[position] = inventory
                cursor+= inventory_len
        if length != cursor:
            print("Metadata length is wrong!")

    def nodeMetadataCompile(self):
        self.nodeMetadataRead = bytearray()
        self.nodeMetadataRead.extend(struct.pack('>B', self.metadata_version))
        self.nodeMetadataRead.extend(struct.pack('>H', len(self.arrayMetadataRead)))
        for position, Metadata in self.arrayMetadataRead.items():
            #print("nokey??? "+type(position))
            self.nodeMetadataRead.extend(struct.pack('>H', position))
            self.nodeMetadataRead.extend(struct.pack('>i', len(Metadata)))
            for key, val in Metadata.items():
                self.nodeMetadataRead.extend(struct.pack('>H', len(key)))
                self.nodeMetadataRead.extend(key)
                self.nodeMetadataRead.extend(struct.pack('>i', len(val)))
                self.nodeMetadataRead.extend(val)
                # So, save in new metadata format?
                self.nodeMetadataRead.append(self.arrayMetadataReadPrivate[position][key])
                    
            self.nodeMetadataRead.extend(self.arrayMetadataReadInventory[position])

    def objectsParse(self):
        #TODO
        return

    def nameIdMappingsParse(self):
        length = len(self.nameIdMappingsRead)
        cursor = 0
        #length already was read
        cursor = 2
        for i in range(0, self.num_name_id_mappings):
            mapping_id = struct.unpack('>H', self.nameIdMappingsRead[cursor:cursor + 2])[0]
            cursor+= 2
            size = struct.unpack('>H', self.nameIdMappingsRead[cursor:cursor + 2])[0]
            cursor+= 2
            self.nameIdMappings[mapping_id] = self.nameIdMappingsRead[cursor:cursor + size]
            cursor+= size
        if length != cursor:
            print("Mapping data length is wrong!")

    def nameIdMappingsCompile(self):
        self.num_name_id_mappings = len(self.nameIdMappings)
        self.nameIdMappingsRead = bytearray()
        self.nameIdMappingsRead.extend(struct.pack('>H', self.num_name_id_mappings))
        for mapping_id, mapping in self.nameIdMappings.items():
            self.nameIdMappingsRead.extend(struct.pack('>H', mapping_id))
            self.nameIdMappingsRead.extend(struct.pack('>H', len(mapping)))
            self.nameIdMappingsRead.extend(mapping)

    def timersParse(self):
        length = len(self.timersRead)
        cursor = 0
        #num already was read
        cursor = 2
        for i in range(0, self.num_of_timers):
            position = struct.unpack('>H', self.timersRead[cursor:cursor + 2])[0]
            cursor+= 2
            self.arrayTimerTimeout[position] = struct.unpack('>i', self.timersRead[cursor:cursor + 4])[0]
            cursor+= 4
            self.arrayTimerElapsed[position] = struct.unpack('>i', self.timersRead[cursor:cursor + 4])[0]
            cursor+= 4
        if length != cursor:
            print("Timer data length wrong!")

    def timersCompile(self):
        self.num_of_timers = len(self.arrayTimerTimeout)
        self.timersRead = bytearray()
        self.timersRead.extend(struct.pack('>H', self.num_of_timers))
        for position, timeout in self.arrayTimerTimeout.items():
            self.timersRead.extend(struct.pack('>H', position))
            self.timersRead.extend(struct.pack('>i', timeout))
            self.timersRead.extend(struct.pack('>i', self.arrayTimerElapsed[position]))
