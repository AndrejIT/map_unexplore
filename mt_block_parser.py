#!/usr/bin/env python

#Licence LGPL v2.1
#Created for version 25
#https://github.com/minetest/minetest/blob/944ffe9e532a3b2be686ef28c33313148760b1c9/doc/mapformat.txt

import struct
import zlib

class MtBlockParser:
    'Allows to read different data from Minetest map v.25 block'
    length = None
    
    version = 25
    flags = None
    content_width = 2
    params_width = 2
    
    nodeDataRead = ''
    arrayParam0 = None
    arrayParam1 = None
    arrayParam2 = None
    
    nodeMetadataRead = ''
    metadata_version = 1
    metadata_count = None
    arrayMetadataTypeId = None
    arrayMetadataRead = None
    
    static_object_version = 0
    static_object_count = None
    objectsRead = ''
    #TODO
    
    timestamp = None
    
    name_id_mapping_version = 0
    num_name_id_mappings = None
    nameIdMappingsRead = ''
    nameIdMappings = None
    
    length_of_timer = 10
    num_of_timers = None
    timersRead = ''
    arrayTimerTimeout = None
    arrayTimerElapsed = None
    
    def __init__(self, blockBlob):
        self.arrayParam0 = {}
        self.arrayParam1 = {}
        self.arrayParam2 = {}
        self.arrayMetadataTypeId = {}
        self.arrayMetadataRead = {}
        self.nameIdMappings = {}
        self.arrayTimerTimeout = {}
        self.arrayTimerElapsed = {}
        self.length = len(blockBlob)
        
        cursor = 0
        if self.version > struct.unpack('B', blockBlob[cursor:cursor + 1])[0]:
            print("Version not supported!")
        cursor+= 1
        self.flags = struct.unpack('B', blockBlob[cursor:cursor + 1])[0]
        cursor+= 1
        if self.content_width != struct.unpack('B', blockBlob[cursor:cursor + 1])[0]:
            print("Content width not supported!")
        cursor+= 1
        if self.params_width != struct.unpack('B', blockBlob[cursor:cursor + 1])[0]:
            print("Params width not supported!")
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
        cursor+= 2
        for i in range(0, self.static_object_count):
            self.objectsRead+= blockBlob[cursor:cursor + 13]
            cursor+= 13
            self.objectsRead+= blockBlob[cursor:cursor + 2]
            data_size = struct.unpack('>H', blockBlob[cursor:cursor + 2])[0]
            cursor+= 2
            self.objectsRead+= blockBlob[cursor:cursor + data_size]
            cursor+= data_size
        self.timestamp = struct.unpack('>I', blockBlob[cursor:cursor + 4])[0]
        cursor+= 4
        if self.name_id_mapping_version != struct.unpack('B', blockBlob[cursor:cursor + 1])[0]:
            print("Name-ID mapping version not supported!")
        cursor+= 1
        self.num_name_id_mappings = struct.unpack('>H', blockBlob[cursor:cursor + 2])[0]
        cursor+= 2
        for i in range(0, self.num_name_id_mappings):
            self.nameIdMappingsRead+= blockBlob[cursor:cursor + 2]
            cursor+= 2
            self.nameIdMappingsRead+= blockBlob[cursor:cursor + 2]
            data_size = struct.unpack('>H', blockBlob[cursor:cursor + 2])[0]
            cursor+= 2
            self.nameIdMappingsRead+= blockBlob[cursor:cursor + data_size]
            cursor+= data_size
        if self.length_of_timer != struct.unpack('B', blockBlob[cursor:cursor + 1])[0]:
            print("Length of timer not supported!")
        cursor+= 1
        self.num_of_timers = struct.unpack('>H', blockBlob[cursor:cursor + 2])[0]
        cursor+= 2
        for i in range(0, self.num_of_timers):
            self.timersRead+= blockBlob[cursor:cursor + 10]
            cursor+= 10
        if self.length != cursor:
            print("Parsed length is wrong!")
        
    def nodeDataParse(self):
        if self.nodeDataRead == None or self.nodeDataRead == '':
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

    def nodeMetadataParse(self):
        if self.nodeMetadataRead == None or self.nodeMetadataRead == '':
            print("No node metadata!")
            return
        length = len(self.nodeMetadataRead)
        cursor = 0
        if self.metadata_version != struct.unpack('>H', self.nodeMetadataRead[cursor:cursor + 2])[0]:
            print("Unsuported metadata version!")
        cursor+= 2
        self.metadata_count = struct.unpack('>H', self.nodeMetadataRead[cursor:cursor + 2])[0]
        cursor+= 2
        for i in range(0, self.metadata_count):
            position = struct.unpack('>H', self.nodeMetadataRead[cursor:cursor + 2])[0]
            cursor+= 2
            self.arrayMetadataTypeId[position] = struct.unpack('>H', self.nodeMetadataRead[cursor:cursor + 2])[0]
            cursor+= 2
            size = struct.unpack('>H', self.nodeMetadataRead[cursor:cursor + 2])[0]
            cursor+= 2
            self.arrayMetadataRead = self.nodeMetadataRead[cursor:cursor + size]
            cursor+= size
        if length != cursor:
            print("Metadata length is wrong!")


    def objectsParse(self):
        #TODO
        return

    def nameIdMappingsParse(self):
        length = len(self.nameIdMappingsRead)
        cursor = 0
        for i in range(0, self.num_name_id_mappings):
            mapping_id = struct.unpack('>H', self.nameIdMappingsRead[cursor:cursor + 2])[0]
            cursor+= 2
            size = struct.unpack('>H', self.nameIdMappingsRead[cursor:cursor + 2])[0]
            cursor+= 2
            self.nameIdMappings[mapping_id] = self.nameIdMappingsRead[cursor:cursor + size]
            cursor+= size
        if length != cursor:
            print("Mapping data length is wrong!")

    def timersParse(self):
        length = len(self.timersRead)
        cursor = 0
        for i in range(0, self.num_of_timers):
            position = struct.unpack('>H', self.timersRead[cursor:cursor + 2])[0]
            cursor+= 2
            self.arrayTimerTimeout[position] = struct.unpack('>i', self.timersRead[cursor:cursor + 4])[0]
            cursor+= 4
            self.arrayTimerElapsed[position] = struct.unpack('>i', self.timersRead[cursor:cursor + 4])[0]
            cursor+= 4
        if length != cursor:
            print("Timer data length wrong!")
