#!/usr/bin/python

import os
import sys
import math
import json
import shutil
from os import listdir
from os.path import isfile, join
from PIL import Image, ImageFilter
import time

start_seconds = int(round(time.time()))

if len( sys.argv ) < 3 :
    print "Usage:"
    print "compile.py <map_name> <tile_size>"
    print "Optionally:"
    print "compile.py <map_name> <tile_size> <pretty> <prefix> <map_dir> <output_dir>"
    exit( 1 )

map_name = sys.argv[ 1 ]
tile_size = int( sys.argv[ 2 ] )
map_dir = ""
output_dir = ""
prefix = ""
pretty = False
if len( sys.argv ) >= 4 :
    pretty = sys.argv[ 3 ]
if len( sys.argv ) >= 5 :
    prefix = sys.argv[ 4 ]
if len( sys.argv ) >= 6 :
    map_dir = sys.argv[ 5 ]
if len( sys.argv ) >= 7 :
    output_dir = sys.argv[ 6 ]


array_files = []
string_path = os.path.dirname( os.path.realpath( __file__ ) ) + "/" + map_dir
if os.path.isdir( string_path ) :
    files = [ f for f in listdir( string_path ) if ( isfile( join( string_path, f ) ) and f.startswith( map_name ) ) ]
    
    if len( files ) == 0 :
        print "No files found"
        exit( 1 )
    file = files[ 0 ]
    current_image = Image.open( string_path + "/" + file )
    dimensions = current_image.size
    if dimensions[ 0 ] % int( tile_size ) != 0 :
        print "Cannot compile: " + string_path + "/" + file
        print "Image width modulus tile_size does not return 0!"
        exit( 1 )
    if dimensions[ 1 ] % int( tile_size ) != 0 :
        print "Cannot compile: " + string_path + "/" + file
        print "Image width modulus tile_size does not return 0!"
        exit( 1 )
    
    tile_width = dimensions[ 0 ] / tile_size
    tile_height = dimensions[ 1 ] / tile_size
    grid = []

    for x in range ( 0, tile_width ):
        row = []
        for y in range ( 0, tile_height ):
            dictionary = {}
            row.append( dictionary )
        y = 0
        grid.append( row )
        
    for file in files :
        if file.startswith( map_name ) :
            current_image = Image.open( string_path + "/" + file )
            current_image = current_image.transpose( Image.FLIP_TOP_BOTTOM )
            if current_image.size != dimensions :
                print "Dimensions mismatch"
                exit( 1 )
            
            pixels = current_image.getdata()
            data_name = file.replace( map_name, '' )
            data_name = data_name.replace( '_', '' )
            data_name = data_name.replace( '.png', '' )
            data_name = data_name.replace( '.jpg', '' )
            y = 0
            array_files.append( file )

            while y < current_image.size[ 1 ] :
                x = 0
                while x < current_image.size[ 0 ] :
                    current_tile = ( int( math.floor( x / tile_size ) ), int( math.floor( y / tile_size ) ) )
                    current_pixel = pixels[ x + ( y * current_image.size[ 0 ] ) ]
                    if current_pixel[ 3 ] != 0 :
                        grid[ current_tile[ 0 ] ][ current_tile[ 1 ] ][ data_name ] = current_pixel
                        x += tile_size
                        continue
                    x += 1
                y += 1

data = {
	"metadata": {
		"files" : array_files,
		"tile_size" : tile_size,
		"map_name" : map_name
	},
	"grid": grid
}
if pretty != False :
	string_grid_json = json.dumps( data, sort_keys=True,indent=4, separators=(',', ': '))
else :
	string_grid_json = json.dumps( data )

with open( output_dir + 'compiled_' + map_name + ".js", "wb" ) as compiled_file:
	compiled_file.write( prefix + string_grid_json )

if output_dir != "" :
	for file in array_files :
		shutil.copy2( string_path + "/" + file, output_dir + file )
        
        
end_seconds = int(round(time.time()))
print "Compilation finished in: " + str(end_seconds-start_seconds) + " seconds"
print "Files processed were:"
print array_files
#image = Image.open("yep.png")
#pixels = list(image.getdata())
#print image.mode
#print pixels[0]
