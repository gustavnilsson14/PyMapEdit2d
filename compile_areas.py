#!/usr/bin/python

import os
import sys
import math
import json
import shutil
from random import randint
from os import listdir
from os.path import isfile, join
from PIL import Image, ImageFilter
import time

start_seconds = int(round(time.time()))

if len( sys.argv ) < 2 :
    print("Usage:")
    print("compile.py <map_name>")
    print("Optionally:")
    print("compile.py <map_name> <pretty> <prefix> <map_dir> <output_dir>")
    exit( 1 )

map_name = sys.argv[ 1 ]
map_dir = ""
output_dir = ""
prefix = ""
pretty = False
if len( sys.argv ) >= 3 :
    pretty = sys.argv[ 2 ]
if len( sys.argv ) >= 4 :
    prefix = sys.argv[ 3 ]
if len( sys.argv ) >= 5 :
    map_dir = sys.argv[ 4 ]
if len( sys.argv ) >= 6 :
    output_dir = sys.argv[ 5 ]


array_files = []
string_path = os.path.dirname( os.path.realpath( __file__ ) ) + "/" + map_dir
areas = {}
if not os.path.isdir( string_path ) :
    print('os.path.isdir fails')
    exit( 1 )

files = [ f for f in listdir( string_path ) if ( isfile( join( string_path, f ) ) and f.startswith( map_name ) ) ]

if len( files ) == 0 :
    print("No files found")
    exit( 1 )
filename = files[ 0 ]
current_image = Image.open( string_path + "/" + filename )
dimensions = current_image.size

def get_rect_from_pixel(image,pos,data_areas):
    x = pos[0]
    y = pos[1]
    x2 = None
    y2 = None
    while x2 == None :
        current_pixel = pixels[ x + ( y * current_image.size[ 0 ] ) ]
        if current_pixel[ 3 ] == 0 or pixel_already_processed((x,y),data_areas):
            x2 = x
        x += 1
    y += 1

    while y2 == None and y < current_image.size[ 1 ]:
        x = pos[0]
        while x < x2 and y2 == None :
            current_pixel = pixels[ x + ( y * current_image.size[ 0 ] ) ]
            if pixel_already_processed((x,y),data_areas):
                return None
            if current_pixel[ 3 ] == 0:
                y2 = y
            x += 1
        y += 1
    if y2 == None:
        return None
    return (pos[0],pos[1],x2,y2)

def pixel_already_processed(pos,rects):
    for rect in rects:
        if pos[0] < rect[0] or pos[0] > rect[2]:
            continue
        if pos[1] < rect[1] or pos[1] > rect[3]:
            continue
        return 1
    return 0

for filename in files :
    if filename.startswith( map_name ) :
        current_image = Image.open( string_path + "/" + filename )
        current_image = current_image.transpose( Image.FLIP_TOP_BOTTOM )
        if current_image.size != dimensions :
            print("Dimensions mismatch")
            exit( 1 )

        pixels = current_image.getdata()
        data_name = filename.replace( map_name, '' )
        data_name = data_name.replace( '_', '' )
        data_name = data_name.replace( '.png', '' )
        data_name = data_name.replace( '.jpg', '' )
        y = 0
        array_files += [filename]
        data_areas = []

        while y < current_image.size[ 1 ] :
            x = 0
            while x < current_image.size[ 0 ] :
                current_pixel = pixels[ x + ( y * current_image.size[ 0 ] ) ]
                if current_pixel[ 3 ] != 0 and not pixel_already_processed((x,y),data_areas):
                    rect = get_rect_from_pixel(current_image,(x,y),data_areas)
                    if rect == None:
                        x += 1
                        continue
                    data_areas += [rect]
                    x += 1
                    continue
                x += 1
            y += 1
        areas[data_name] = data_areas

data = {
	"metadata": {
		"files": array_files,
		"map_name": map_name
	},
	"areas": areas
}
print(data)
if pretty != False :
	string_grid_json = json.dumps( data, sort_keys=True,indent=4, separators=(',', ': '))
else :
	string_grid_json = json.dumps( data )

with open( output_dir + 'compiled_' + map_name + ".js", "wb" ) as compiled_file:
	compiled_file.write( bytes(prefix + string_grid_json,'utf8') )

if output_dir != "" :
	for file in array_files :
		shutil.copy2( string_path + "/" + file, output_dir + file )


end_seconds = int(round(time.time()))
print("Compilation finished in: " + str(end_seconds-start_seconds) + " seconds")
print("Files processed were:")
print(array_files)
#image = Image.open("yep.png")
#pixels = list(image.getdata())
#print image.mode
#print pixels[0]
