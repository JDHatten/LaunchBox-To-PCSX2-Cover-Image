#!/usr/bin/python
# -*- coding: utf-8 -*-

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
LaunchBox To PCSX2 Cover Image
  Verion 1.0
  by JDHatten
    
    Description:
        This script will copy and resize PlayStation 2 LaunchBox images and save them
        to the PCSX2 cover image folder.
    
    To Use:
        First, run the script and make sure root path settings are correct.
        Then drop or type a path to a PS2 game disc into the command prompt.
        -OR-
        Type a complete or partial game title into the command prompt.
    
    Note:
        Type "Help" in the command prompt for additional information and commands.

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# Set this to False if you just want to drop a game disc file, copy the associated image, and close.
# Note: "Drop" means to click, drag and drop a game disc file onto this file/script.
loop_script = True

# Always use previous selected options.
# Note: This only applies to drops and is usful for fast changes when "loop_script" is False.
always_use_previous_choices = False



### Don't edit below this line unless you know what your doing. ###



import configparser as CP
import math as Math
from pathlib import Path, PurePath
try:
    from PIL import Image, UnidentifiedImageError
    pillow_installed = True
except ModuleNotFoundError:
    pillow_installed = False
from os import environ as ENV, get_terminal_size as TSize
import re as RE
from shutil import copy2 as CopyFile
from subprocess import Popen as Open
import sys as System
import tkinter as TK
from tkinter import filedialog as FileDialog
import xml.etree.ElementTree as ET


# Note: Many of these variables below are defaults and any changes made while this script
#       is running will overwrite these defaults and save them to file.


# Path to LaunchBox's and PCSX2's root install directories.
# Note: If these default paths are wrong, this script will ask for the actual paths and they
#       will be saved in the XML settings_file.
launchbox_root = rf'{ENV.get("ProgramFiles")}\LaunchBox'
pcsx2_root = rf'{ENV.get("ProgramFiles")}\PCSX2'

# Choose what category of images to use. ("Box - Front" is the front cover box art.)
# Note: More categories can be found in LaunchBox's image directories.
#       "Box - 3D", "Box - Back", "Box - Front - Reconstructed", "Disc", "Clear Logo",
#       "Screenshot - Game Title", "Screenshot - Gameplay", "Cart - Front",...
launchbox_media_type = 'Box - Front'

# It's recommended you resize any large images to 720p or smaller.
# Enter 0 if you do not want the image file resized.
# Note: If the LaunchBox image is smaller than the resize, it will not be modified at all.
resize_cover_image = 720

# If your always changeing PCSX2 cover images, save time setting this to True.
always_overwrite = False

# Auto-search for both Arabic and Roman numerals ("2" will also search for "II" and vice-versa).
# Note: Only works for numbers between 1-20 or I-XX.
search_both_number_systems = True

# Path to LaunchBox's Sony PlayStation 2 XML file. (Shouldn't need changing)
launchbox_ps2_xml = rf'{launchbox_root}\Data\Platforms\Sony Playstation 2.xml'

# Path to LaunchBox's Platform XML file. (Shouldn't need changing)
launchbox_platform_xml = rf'{launchbox_root}\Data\Platforms.xml'

# File with database scraped list of all PS2 game titles usable in PCSX2.
pcsx2_game_database = rf'{pcsx2_root}\resources\GameIndex.yaml'

# File with all user's PS2 games scanned and recognized by PCSX2.
pcsx2_game_list_file = rf'{pcsx2_root}\cache\gamelist.cache'

# Used to get any custom game titles and update the "pcsx2_user_game_list".
# Note: PCSX2 stores file paths in config (ini file) section headings. This is bad for file names
#       using [square brackets], which is a common naming convention for modified/hacked games.
#       While this script can account for this error and still name the image with the proper
#       custom name, it won’t show anyways. So it will just name the image whatever wrong name
#       PCSX2 has chosen so it will at least show up in the emulator. Hopefully the PCSX2 devs
#       fix this soon, maybe use a YAML or XML file instead of an ini file.
pcsx2_custom_game_title_file = rf'{pcsx2_root}\inis\custom_properties.ini'

# Used to get the current PCSX2 cover image folder.
pcsx2_settings_file = rf'{pcsx2_root}\inis\PCSX2.ini'

# PCSX2's default cover image directory. Only used as a fallback.
pcsx2_image_folder = rf'{pcsx2_root}\PCSX2\covers'

# LaunchBox's default PS2 image directory. Only used as a fallback.
launchbox_image_folder = rf'{launchbox_root}\Images\Sony Playstation 2\{launchbox_media_type}'

# Set to False to add foreign character title names to the full list of "searchable" PS2 games.
# Note: Only useful when matching games between LaunchBox and PCSX2 fail and there are foreign
#       characters in the game titles to search through.
only_english_characters_in_game_list = True

# Only recognize Roman numerals if they are capitalized/uppercase.
uppercase_roman_numerals_only = True

ROOT = Path(__file__).parent
pcsx2_game_database = Path(pcsx2_game_database)
pcsx2_custom_game_title_file = Path(pcsx2_custom_game_title_file)
pcsx2_settings_file = Path(pcsx2_settings_file)
full_pcsx2_game_list_file = ROOT / 'full_pcsx2_game_list.txt'
settings_file = ROOT / f'{Path(__file__).stem}-Settings.xml'
last_ps2_directory = ROOT
pcsx2_full_game_list = []
pcsx2_user_game_list = []       # [ [ ID, TITLE, DISC_PATH ],...]
launchbox_game_list = []        # [ [ ID, TITLE, DISC_PATH ],...]
launchbox_media_type_list = []  # [ [ TYPE, PATH ],...]
supported_images = ['.jpg','.jpeg', '.jpe', '.png', '.webp']
roman_numerals_list = ['0','I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV','XVI','XVII','XVIII','XIX','XX']
arabic_numerals_list = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20']
re_roman_numerals = RE.compile(r'\b(xx|xix|xviii|xvii|xvi|xiv|xiii|xii|xi|ix|viii|vii|vi|iv|xv|x|v|iii|ii|i)\b')
RE_ROMAN_NUMERALS = RE.compile(r'\b(XX|XIX|XVIII|XVII|XVI|XIV|XIII|XII|XI|IX|VIII|VII|VI|IV|XV|X|V|III|II|I)\b')
re_arabic_numerals = RE.compile(r'\b([0-9]|1[0-9]|20)\b')

# Constants
SCRIPT_TITLE   = 'LaunchBox To PCSX2 Cover Image'
SCRIPT_VERSION = 'v1.0'
SCRIPT_CREATOR = 'by JDHatten'
MEDIA_TYPE_ALL = 'Choose From Any Category (All)'

# Game List Data Indexes
ID = 0          # -> String
TITLE = 1       # -> String
DISC_PATH = 2   # -> String or List

# Media Type Indexes
TYPE = 0        # -> String
PATH = 1        # -> String

# Image Dimension Indexes
WIDTH = 0
HEIGHT = 1

# Image Modifier Indexes
MODIFIER = 0
NUMBER = 1

# Image Modifiers
NO_CHANGE = 0          # Keep size as is.
CHANGE_TO = 1          # Change to a specific size.
MODIFY_BY_PIXELS = 2   # Add/subtract to/from current size.
MODIFY_BY_PERCENT = 3  # Percent of current size (50% = current size * 0.5).
UPSCALE = 4            # Only increase to specific size (keep as is if current size is larger).
DOWNSCALE = 5          # Only decrease to specific size (keep as is if current size is smaller).

# Resampling Filters
NEAREST = 0   # Default
BILINEAR = 1  # 
BICUBIC = 2   # 

# Settings
LAUNCHBOX_ROOT = 0
PCSX2_ROOT = 1
LAUNCHBOX_MEDIA_TYPE = 2
RESIZE_COVER_IMAGE = 3
ALWAYS_OVERWRITE = 4
SEARCH_BOTH_NUMBER_SYSTEMS = 5
DEFAULT_SETTINGS = 6
LAST_PS2_DIRECTORY = 99


### Update all paths related to a change in LaunchBox or PCSX2 root paths.
###     (changed_path) LAUNCHBOX_ROOT or PCSX2_ROOT.
def updatePathsUsing(changed_path: int):
    global launchbox_ps2_xml
    global launchbox_platform_xml
    global pcsx2_game_database
    global pcsx2_game_list_file
    global pcsx2_custom_game_title_file
    global pcsx2_settings_file
    global pcsx2_image_folder
    global launchbox_image_folder
    
    if changed_path == PCSX2_ROOT:
        
        # Defaults
        pcsx2_game_database = rf'{pcsx2_root}\resources\GameIndex.yaml'
        pcsx2_game_list_file = rf'{pcsx2_root}\cache\gamelist.cache'
        pcsx2_custom_game_title_file = rf'{pcsx2_root}\inis\custom_properties.ini'
        pcsx2_settings_file = rf'{pcsx2_root}\inis\PCSX2.ini'
        pcsx2_image_folder = rf'{pcsx2_root}\PCSX2\covers'
        
        # Build list of PCSX2 game titles
        # Note: This is a must to properly match naming conventions between LaunchBox and PCSX2.
        if createListOfPCSX2Games(): # -> pcsx2_user_game_list
            
            # Get any needed PCSX2 folder settings
            if Path(pcsx2_settings_file).exists():
                try:
                    pcsx2_settings = CP.ConfigParser(strict=False)
                    pcsx2_settings.read(pcsx2_settings_file)
                    pcsx2_game_list_file = pcsx2_settings['Folders']['Cache']
                    pcsx2_image_folder = pcsx2_settings['Folders']['Covers']
                    pcsx2_game_list_file = resolvePath(pcsx2_game_list_file, pcsx2_root)
                    pcsx2_image_folder = resolvePath(pcsx2_image_folder, pcsx2_root)
                    return
                except CP.Error as e:
                    print(f'ERROR: Failed reading PCSX2 settings file: {e}')
                except Exception as e:
                    print(f'ERROR: Failed reading PCSX2 settings file: {e}')
            else:
                print(f'ERROR: The file "{pcsx2_settings_file}" was not found.')
            print('WARNING: Default PCSX2 folders will be used.')
        else:
            print('ERROR: Failed to find a list of PCSX2 game titles.')
    
    if changed_path == LAUNCHBOX_ROOT:
        
        # Defaults
        launchbox_ps2_xml = rf'{launchbox_root}\Data\Platforms\Sony Playstation 2.xml'
        launchbox_platform_xml = rf'{launchbox_root}\Data\Platforms.xml'
        launchbox_image_folder = rf'{launchbox_root}\Images\Sony Playstation 2\{launchbox_media_type}'
        
        try:
            launchbox_ps2_xml_root = ET.parse(launchbox_ps2_xml).getroot()
            launchbox_platform_xml_root = ET.parse(launchbox_platform_xml).getroot()
            
            # Build list of LaunchBox game titles and their disc paths
            if len(launchbox_game_list) == 0:
                for lb_game in launchbox_ps2_xml_root.findall('Game'):
                    lb_game_id = lb_game.find('ID').text
                    lb_game_title = lb_game.find('Title').text
                    lb_game_path = lb_game.find('ApplicationPath').text
                    launchbox_game_list.append([ lb_game_id, lb_game_title, [lb_game_path] ])
                    
                for lb_game in launchbox_ps2_xml_root.findall('AdditionalApplication'):
                    lb_emu_id = lb_game.find('EmulatorId').text
                    lb_game_id = lb_game.find('GameID').text
                    lb_game_path = lb_game.find('ApplicationPath').text
                    if lb_emu_id: # Check if this is a game disc connected to an emulator.
                        for game in launchbox_game_list:
                            # Update the game with another disc path
                            # (Multi-disc game: additional content, alt version/region, hacked/modded, etc)
                            if game[ID] == lb_game_id:
                                if lb_game_path not in game[DISC_PATH]:
                                    game[DISC_PATH].append(lb_game_path)
            
            # Get paths to LaunchBox's PS2 image folders.
            launchbox_media_type_list.clear()
            for platform_folder in launchbox_platform_xml_root.findall('PlatformFolder'):
                media_type = platform_folder.find('MediaType').text
                folder_path = platform_folder.find('FolderPath').text
                platform = platform_folder.find('Platform').text
                if platform == 'Sony Playstation 2':
                    launchbox_media_type_list.append([ media_type, folder_path ])
                    if media_type == launchbox_media_type: # Get user chosen image category path
                        launchbox_image_folder = folder_path
            launchbox_media_type_list.append([MEDIA_TYPE_ALL,'.ALL']) # If selected, will loop all types/paths
        
        except IOError as e:
            print(f"ERROR: Failed reading XML file: {e}")
        except OSError as e:
            print(f"ERROR: Operating system error: {e}")
        except Exception as e:
            print(f'ERROR: {e}')


### Check if root paths are correct and if not ask user to update settings.
###     --> Returns a [bool] Pass or Fail
def rootPathCheck():
    if (not Path(launchbox_root + r'\LaunchBox.exe').exists() or not
        (
            Path(pcsx2_root + r'\pcsx2.exe').exists() or
            Path(pcsx2_root + r'\pcsx2-qtx64-avx2.exe').exists() or
            Path(pcsx2_root + r'\pcsx2x64-avx2.exe').exists()
        )):
        print(f'\nWARNING: LaunchBox and/or PCSX2 root paths do not exist.')
        print(f'         Please update them now.')
        showSettingsMenu()
        return False
    else:
        return True


### Resolve a relative path to a full absolute path.
###     (path) Any path.
###     (root) The relevant root or parent path.
###     --> Returns a [Path] Absolute
def resolvePath(path: str, root: str) -> Path:
    path = Path(path)
    root = Path(root)
    if not path.exists():
        path = Path(root / path).resolve()
    return path


### Resize a PS2 game cover image and save it.
###     (image_path) A path to an image file.
###     (new_height) The new height to resize the image to. Aspect ratio will be kept and size/scale will only be decreased, not increase.
###     (save_path) A path to save the new resized image file. If not provided the image file will be overwritten.
###     --> Returns a [bool]
def resizeCoverImage(image_path: Path, new_height: int = 720, save_path: Path = Path()) -> bool:
    if not pillow_installed:
        print(f'WARNING: The Pillow (PIL) Python module is not installed and is required to resize images.')
        print(f'To install Pillow open a command prompt and first enter:')
        print(f'  python3 -m pip install --upgrade pip')
        print(f'To make sure PIP is upgraded to the latest version then enter...')
        print(f'  python3 -m pip install --upgrade Pillow')
        print(f'\nNote: "python3" is assumed, could also be "python.exe" or a direct path to the application.')
        return False
    
    if image_path.suffix.lower() not in supported_images:
        print(f'WARNING: "{image_path.suffix}" is not a supported image file type.')
        return False
    
    image_source = Image.open(image_path)
    
    if image_source.height <= new_height:
        print(f'Image height already {new_height}p or smaller.')
        return False
    
    width_change = NO_CHANGE
    height_change = (CHANGE_TO, new_height)
    
    print(f'Orginal Image Size: {image_source.width} x {image_source.height}')
    
    resized_image = resizeImage(image_source, width_change, height_change, True, BICUBIC)
    
    if image_source:
        try:
            params = {
                'quality' : 95, # JPEG
                'compress_level' : 9, # PNG
            }
            if save_path == Path():
                resized_image.save(image_path, **params)
            else:
                resized_image.save(save_path, **params)
            print(f'New Image Size:      {resized_image.width} x {resized_image.height}')
            return True
        except (OSError, ValueError) as e:
            print(f'ERROR: Failed To Save Image: {e}')
            return False


### Resize an image.
###     (image) An Image that is to be resized.
###     (width_change) A Tuple with specific data on how to modify the width of an image.
###     (height_change) A Tuple with specific data on how to modify the height of an image.
###     (keep_aspect_ratio) Keep aspect ratio only if one size, width or height, has changed.
###     (resample) Resampling filter to use while modifying an Image.
###     --> Returns a [Image]
def resizeImage(image: Image, width_change: (int, int), height_change: (int, int), keep_aspect_ratio: bool = True, resample: int = NEAREST) -> Image:
    if resample == BILINEAR:  resample = Image.Resampling.BILINEAR
    elif resample == BICUBIC: resample = Image.Resampling.BICUBIC
    else:                     resample = Image.Resampling.NEAREST
    
    if width_change or height_change:
        new_width, new_height = modifyImageSize((image.width, image.height), (width_change, height_change), keep_aspect_ratio)
        image = image.resize((new_width, new_height), resample=resample, box=None, reducing_gap=None)
    
    return image


### Modify the size/shape of an image.
###     (org_image_shape) The height and width of the orginal image. ( Width, Height )
###     (image_size_modifications) How to modify the height and width of the orginal image. [ ( Modifier, Width ), ( Modifier, Height ) ]
###     (keep_aspect_ratio) True or False
###     --> Returns a [Tuple] (Height, Width)
def modifyImageSize(org_image_shape: (int, int), image_size_modifications: list, keep_aspect_ratio: bool = True) -> (int, int):
    # Width
    if type(image_size_modifications[WIDTH]) is tuple:
        
        if image_size_modifications[WIDTH][MODIFIER] == NO_CHANGE:
            new_width = org_image_shape[WIDTH]
        
        if image_size_modifications[WIDTH][MODIFIER] == CHANGE_TO:
            new_width = image_size_modifications[WIDTH][NUMBER]
        
        if image_size_modifications[WIDTH][MODIFIER] == MODIFY_BY_PERCENT:
            if type(image_size_modifications[WIDTH][NUMBER]) == str:
                percent_number = RE.search(r'\d*\.?\d*', image_size_modifications[WIDTH][NUMBER])
                if percent_number:
                    multipler = float(percent_number).group().strip() / 100
                    new_width = org_image_shape[WIDTH] * multipler
                else:
                    print(f'ERROR: Can\'t decipher what kind of number this is: {image_size_modifications[WIDTH]}')
                    new_width = org_image_shape[WIDTH]
            else:
                multipler = image_size_modifications[WIDTH][NUMBER] / 100
                new_width = org_image_shape[WIDTH] * multipler
        
        if image_size_modifications[WIDTH][MODIFIER] == MODIFY_BY_PIXELS:
            new_width = org_image_shape[WIDTH] + image_size_modifications[WIDTH][NUMBER]
        
        if image_size_modifications[WIDTH][MODIFIER] == UPSCALE:
            if org_image_shape[WIDTH] < image_size_modifications[WIDTH][NUMBER]:
                new_height = image_size_modifications[WIDTH][NUMBER]
            else:
                new_height = org_image_shape[WIDTH]
        
        if image_size_modifications[WIDTH][MODIFIER] == DOWNSCALE:
            if org_image_shape[WIDTH] > image_size_modifications[WIDTH][NUMBER]:
                new_height = image_size_modifications[WIDTH][NUMBER]
            else:
                new_height = org_image_shape[WIDTH]
    
    elif image_size_modifications[WIDTH] != NO_CHANGE:
        new_width = image_size_modifications[WIDTH]
    
    else:
        new_width = org_image_shape[WIDTH]
    
    # Height
    if type(image_size_modifications[HEIGHT]) is tuple:
        
        if image_size_modifications[HEIGHT][MODIFIER] == NO_CHANGE:
            new_height = org_image_shape[HEIGHT]
        
        if image_size_modifications[HEIGHT][MODIFIER] == CHANGE_TO:
            new_height = image_size_modifications[HEIGHT][NUMBER]
        
        if image_size_modifications[HEIGHT][MODIFIER] == MODIFY_BY_PERCENT:
            if type(image_size_modifications[HEIGHT][NUMBER]) == str:
                percent_number = RE.search(r'\d*\.?\d*', image_size_modifications[HEIGHT][NUMBER])
                if percent_number:
                    multipler = float(percent_number.group().strip()) / 100
                    new_height = org_image_shape[HEIGHT] * multipler
                else:
                    print(f'ERROR: Can\'t decipher what kind of number this is: {image_size_modifications[HEIGHT]}')
                    new_height = org_image_shape[HEIGHT]
            else:
                multipler = image_size_modifications[HEIGHT][NUMBER] / 100
                new_height = org_image_shape[HEIGHT] * multipler
        
        if image_size_modifications[HEIGHT][MODIFIER] == MODIFY_BY_PIXELS:
            new_height = org_image_shape[HEIGHT] + image_size_modifications[HEIGHT][NUMBER]
        
        if image_size_modifications[HEIGHT][MODIFIER] == UPSCALE:
            if org_image_shape[HEIGHT] < image_size_modifications[HEIGHT][NUMBER]:
                new_height = image_size_modifications[HEIGHT][NUMBER]
            else:
                new_height = org_image_shape[HEIGHT]
        
        if image_size_modifications[HEIGHT][MODIFIER] == DOWNSCALE:
            if org_image_shape[HEIGHT] > image_size_modifications[HEIGHT][NUMBER]:
                new_height = image_size_modifications[HEIGHT][NUMBER]
            else:
                new_height = org_image_shape[HEIGHT]
    
    elif image_size_modifications[HEIGHT] != NO_CHANGE:
        new_height = image_size_modifications[HEIGHT]
    
    else:
        new_height = org_image_shape[HEIGHT]
    
    # Aspect Ratio
    if keep_aspect_ratio and image_size_modifications[WIDTH] == NO_CHANGE and image_size_modifications[HEIGHT] != NO_CHANGE :
        factor_w = org_image_shape[WIDTH] / org_image_shape[HEIGHT]
        new_width = org_image_shape[WIDTH] - (org_image_shape[HEIGHT] - new_height) * factor_w
    
    elif keep_aspect_ratio and image_size_modifications[HEIGHT] == NO_CHANGE and image_size_modifications[WIDTH] != NO_CHANGE:
        factor_h = org_image_shape[HEIGHT] / org_image_shape[WIDTH]
        new_height = org_image_shape[HEIGHT] - (org_image_shape[WIDTH] - new_width) * factor_h
    
    new_width = round(new_width)
    new_height = round(new_height)
    
    return new_width, new_height


### Find and return the index of the first (or n-th) occurrence of a character in a string.
###     (character) Text character to search for in a string.
###     (in_string) The string to search.
###     (n) How many occurrences to find before ending search.
###     --> Returns a [int] Index
def getIndexOf(character: str, in_string: str, n: int = 1) -> int:
    start = in_string.find(character)
    while start >= 0 and n > 1:
        start = in_string.find(character, start+len(character))
        n -= 1
    return start


### Find and return the index of the last (or n-th in reverse) occurrence of a character in a string.
###     (character) Text character to search for in a string.
###     (in_string) The string to search.
###     (n) How many occurrences to find before ending search.
###     --> Returns a [int] Index
def getLastIndexOf(character: str, in_string: str, n: int = 1) -> int:
    start = in_string.rfind(character)
    while start >= 0 and n > 1:
        start = in_string.rfind(character, 0, start)
        n -= 1
    return start


### Find and return the index of the first occurrence of a value in a list.
###     (value) The value to search for in a list.
###     (in_list) The list to search through.
###     (multi_level_key) Preform search in a 2nd level deep list using this key/index.
###     --> Returns a [int] Index
def getListIndexOf(value: str, in_list: list, multi_level_key: int = -1) -> int:
    i = -1
    for item in in_list:
        i += 1
        if multi_level_key > -1:
            if value == str(item[multi_level_key]):
                return i
        else:
            if value == str(item):
                return i
    return -1


### Get a PCSX2 game title from a game id/serial or disc path.
###     (value) A game id/serial or disc path.
###     (key) Key repersenting the value ID or DISC_PATH.
###     --> Returns a [str] Game Title
def getPCSX2GameTitleFrom(value: str, key: int) -> str:
    i = getListIndexOf(value, pcsx2_user_game_list, key)
    if i > -1:
        return pcsx2_user_game_list[i][TITLE]
    else:
        return ''


### Create a selection menu with options for user to choose from.
###     (labels) A list of lines of strings describing the menu.
###     (choices) A list options for the user to select.
###     (not_found_choice) Optional selection string to signify "none of the above options is correct".
###     (columns) Print out options in multiple columns (up to a maximum menu width).
###     --> Returns a [int]
def selectionMenu(labels: list, choices: list, not_found_choice: str = '', columns: int = 1) -> int:
    first_choice = 0 if len(not_found_choice) else 1
    max_column_width = 0
    
    if columns > 1:
        for choice in choices:
            length = len(choice) + 8
            if length > max_column_width:
                max_column_width = length
    
    while True:
        n = 0
        row = ''
        
        # If current menu/terminal width is too small for multiple columns, remove a column.
        current_column_count = columns
        while current_column_count > 1 and TSize().columns < max_column_width * current_column_count:
            current_column_count -= 1
        
        for label in labels:
            print(f'{label}')
        
        for choice in choices:
            n += 1
            row += f'  {n}.) {choice}'
            col = n % current_column_count # 0 = last column
            
            if n >= current_column_count and col == 0:
                print(row)
                row = ''
            else:
                if len(choices) == n:
                    print(row) # Last row
                else:
                    row_length = len(row)
                    max_length = max_column_width * col
                    if row_length < max_length:
                        extra_spaces_count = max_length - row_length
                        for s in range(extra_spaces_count):
                            row += ' '
        
        if first_choice == 0:
            print(f'  0.) {not_found_choice}')
        
        try:
            selection = input('\n  Your Selection #: ')
            
            # Allow the use of the "show" command here.
            if selection.lower() == 'show launchbox' or selection.lower() == 'show lb':
                openDirectory(launchbox_image_folder)
                continue
            elif selection.lower() == 'show pcsx2' or selection.lower() == 'show ps':
                openDirectory(pcsx2_image_folder)
                continue
            elif selection == '*': # Cancel
                selection = 0
            
            selection = int(selection)
            if first_choice <= selection <= n:
                return selection
            else:
                print('  Your selected number is out of range. Please try again.\n')
        
        except ValueError:
            print('  Invalid input. Please enter a number.\n')


### Create a selection menu with options for user to choose from. Multiple choices can be made separated with a comma (1,2,3).
###     (labels) A list of lines of strings describing the menu.
###     (choices) A list options for the user to multi-select.
###     (not_found_choice) Optional selection string to signify "none of the above options is correct".
###     (columns) Print out options in multiple columns (up to a maximum menu width).
###     --> Returns a [list] of user selections
def multiSelectionMenu(labels: list, choices: list, not_found_choice: str = '', columns: int = 1) -> list:
    first_choice = 0 if len(not_found_choice) else 1
    max_column_width = 0
    
    if columns > 1:
        for choice in choices:
            length = len(choice) + 8
            if length > max_column_width:
                max_column_width = length
    
    while True:
        error = False
        n = 0
        row = ''
        
        # If current menu/terminal width is too small for multiple columns, remove a column.
        current_column_count = columns
        while current_column_count > 1 and TSize().columns < max_column_width * current_column_count:
            current_column_count -= 1
        
        for label in labels:
            print(f'{label}')
        
        for choice in choices:
            n += 1
            row += f'  {n}.) {choice}'
            col = n % columns # 0 = last column
            
            if n >= columns and col == 0:
                print(row)
                row = ''
            else:
                if len(choices) == n:
                    print(row) # Last row
                else:
                    row_length = len(row)
                    max_length = max_column_width * col
                    if row_length < max_length:
                        extra_spaces_count = max_length - row_length
                        for s in range(extra_spaces_count):
                            row += ' '
        
        if first_choice == 0:
            print(f'  0.) {not_found_choice}')
        
        try:
            user_selections = input('\n  Your Selection(s) #: ').replace(' ', '').split(',')
            user_selections = [int(s) for s in user_selections]
            
            for selection in user_selections:
                if selection == 0 and first_choice == 0:
                    return []
                if selection < first_choice or selection > n:
                    print('  One of your selected numbers is out of range. Please try again.\n')
                    error = True
                    break
            
            if not error:
                return user_selections
            
        except ValueError:
            print('  Invalid input. Please enter numbers only.\n')


### Build PCSX2 game list consisting of user PS2 games. Also a builds a full list of games for fallback searching.
###     (sort) Sort full list of games alphabetically.
###     --> Returns a [bool] Success or Failure
def createListOfPCSX2Games(sort: bool = False) -> bool:
    if_error_file_path = pcsx2_game_database
    
    # The data from below cache file can reliably read game id/serials and disc paths, but not game titles.
    # So proper titles will be obtained from the full list of PS2 games using the game id.
    if len(pcsx2_user_game_list) == 0:
        try:
            with open(pcsx2_game_list_file, 'r', encoding='ISO-8859-1') as game_list_file:
                
                game_list_file_contents = game_list_file.read()
                
                # Find each disc path and prepend a new-line (matchs up to next path on same line or end of line)
                game_list_file_contents = RE.sub(r'(\w:\\.*?)(?=\w:|\n)', r'\n\1', game_list_file_contents)
                
                # Find each game id, remove characters proceeding id and append a new-line after
                game_list_file_contents = RE.sub(r'.*(\w{4}-\d{5})(?<!$)', r'\1\n', game_list_file_contents)
                
                # Now that each ID, TITLE, and DISC_PATH are seperated on different lines...
                temp_game_list = game_list_file_contents.split('\n')
                next_line = DISC_PATH
                
                for line in temp_game_list:
                    line = line.strip()
                    
                    if next_line == DISC_PATH:
                        path = Path(line)
                        if path.exists():
                            pcsx2_user_game_list.append(['','',path])
                            next_line = ID
                    
                    elif next_line == ID:
                        if len(line) > 1:
                            pcsx2_user_game_list[-1][ID] = line
                            next_line = TITLE
                    
                    elif next_line == TITLE:
                        if len(line) > 1:
                            pcsx2_user_game_list[-1][TITLE] = line # May have extra characters, only use for comparision/place holder
                            next_line = DISC_PATH
                
                '''# Print List Test
                printGames('PCSX2', True)
                
                file_path = ROOT / 'temp.txt'
                with open(file_path, 'w', encoding='ISO-8859-1') as f:
                    f.write(game_list_file_contents)
                #'''#
        
        except FileNotFoundError:
            print(f'ERROR: The file "{pcsx2_game_list_file}" was not found.')
            return False
        except Exception as e:
            print(f'ERROR: {e}')
            return False
    
    # Build full list of PS2 games, while also updating "pcsx2_user_game_list" with proper title names.
    if len(pcsx2_full_game_list) == 0:
        try:
            with open(pcsx2_game_database, 'r', encoding='utf-8') as file:
                current_user_game_index = -1
                for line in file:
                    
                    game_id_match = RE.search(r'(\w{4}-\d{5})', line)
                    game_title_match = RE.search('^\s\sname:\s\"(.*?)\"', line)
                    game_title_eng_match = RE.search('^\s\sname-en:\s\"(.*?)\"', line)
                    current_game_title = ''
                    
                    # New game found when a new ID is found.
                    if game_id_match:
                        current_game_id = game_id_match.group(0)
                        current_user_game_index = getListIndexOf(current_game_id, pcsx2_user_game_list, ID)
                    
                    # Next line may be a title
                    elif game_title_match:
                        current_game_title = game_title_match.group(1)
                        
                        # Add to full game list
                        if current_game_title not in pcsx2_full_game_list:
                            pcsx2_full_game_list.append(current_game_title)
                    
                    # Next line may be an English title
                    elif game_title_eng_match:
                        current_game_title = game_title_eng_match.group(1)
                        
                        # Add to full game list
                        if only_english_characters_in_game_list:
                            # Replace the non-English title above (last added).
                            if current_game_title not in pcsx2_full_game_list:
                                pcsx2_full_game_list[-1] = current_game_title
                            else:
                                pcsx2_full_game_list.pop(-1)
                        elif current_game_title not in pcsx2_full_game_list:
                            pcsx2_full_game_list.append(current_game_title)
                    
                    if current_game_title != '': # If an English title exists, it will overwrite previous non-English title.
                        
                        # Update the user game list with new title if matching ID found.
                        if len(pcsx2_user_game_list) > current_user_game_index > -1:
                            pcsx2_user_game_list[current_user_game_index][TITLE] = current_game_title
            
            if sort:
                pcsx2_full_game_list.sort()
            
            '''# Save full list of games to a file
            if not full_pcsx2_game_list_file.exists():
                list_of_games = '\n'.join(pcsx2_full_game_list)
                if_error_file_path = full_pcsx2_game_list_file
                with open(full_pcsx2_game_list_file, 'w', encoding='utf-8') as f:
                    f.write(list_of_games)
            #'''#
        
        except FileNotFoundError:
            print(f'ERROR: The file "{if_error_file_path}" was not found.')
            return False
        except Exception as e:
            print(f'ERROR: {e}')
            return False
    
    # Update "pcsx2_user_game_list" with any custom titles (special versions/betas/hacks/mods/etc.).
    custom_titles = CP.ConfigParser(strict=False)
    try:
        custom_titles.read(pcsx2_custom_game_title_file)
        
        for disc_path in custom_titles.sections():
            if 'Title' in custom_titles[disc_path]:
                custom_game_title = custom_titles.get(disc_path, 'Title')
                ## Skip custom disc names with square bracket characters.
                ## This is a temporary fix, REMOVE if PCSX2 fixes its custom title issue.
                if custom_game_title.find('[') == -1 and custom_game_title.find(']') == -1:
                    i = getListIndexOf(disc_path, pcsx2_user_game_list, DISC_PATH)
                    pcsx2_user_game_list[i][TITLE] = custom_game_title
    
    except CP.Error as e:
        print(rf'Error reading "{pcsx2_custom_game_title_file.name}": {e}')
        print('Custom PCSX2 game titles will not be shown or used.')
    except Exception as e:
        print(f'ERROR: {e}')
        print('Custom PCSX2 game titles will not be shown or used.')
        # Note: It's ok if this fails... return True
    
    return True


### Search a list of games using any of the words in the provided string.
###     (search_words) The words to search for in a list.
###     (in_game_title_list) The list to search through.
###     (multi_level_key) Preform search in a 2nd level deep list using this key/index.
###     --> Returns a [list, list]
def searchFor(search_words: str, in_game_title_list: list, multi_level_key: int = -1) -> (list, list):
    full_matched_list = []
    high_probability_list = []
    re_flags = RE.IGNORECASE
    if uppercase_roman_numerals_only:
        re_flags = 0
    
    # Split and clean-up search words
    segmented_game_title = (
        search_words.replace(':', '').replace(' -', '').replace(' &', '').replace('(', '')
        .replace(')', '').replace('[', '').replace(']', '').replace('"', '').replace('\\', ' ')
        .replace('/', ' ').replace(',', ' ').split()
    )
    
    searchable_title_words = []
    for word in segmented_game_title:
        # Only search for numbers and 3+ letter words (unless only one word).
        if RE.fullmatch(r'\d+|I|II|IV|V|VI|IX|X|XI|XV|XX', word, flags=re_flags):
            searchable_title_words.append(word)
        elif (len(word) > 2) or len(segmented_game_title) == 1:
            searchable_title_words.append(word.lower())
    
    #print(f'\nsearchable_title_words: {searchable_title_words}')
    
    # Search list for 50% or more of the usable search words.
    for game in in_game_title_list:
        game_title = ''
        if multi_level_key > -1:
            game_title = game[multi_level_key].strip()
        else:
            game_title = game.strip()
        
        found_words = 0
        skipped_words = 0
        not_found_words = 0
        for word in searchable_title_words:
            
            if RE_ROMAN_NUMERALS.fullmatch(word):
                searchable_game_title = game_title
            else:
                searchable_game_title = game_title.lower()
            
            if word in searchable_game_title:
                # "The" and numbers will give too many results if they are the only words found.
                # Note: Single word searches (in searchable_title_words) will never be skipped.
                if RE.fullmatch(r'the|\d+|I|II|IV|V|VI|IX|X|XI|XV|XX', word, flags=re_flags):
                    skipped_words += 1
                found_words += 1
            else:
                not_found_words += 1
        
        if found_words == len(searchable_title_words): # All Words Matched
            if game_title not in full_matched_list:
                if multi_level_key > -1:
                    full_matched_list.append(game)
                else:
                    full_matched_list.append(game_title)
        else:
            # Tweaks to what can be included in the high_probability_list.
            total_words = len(searchable_title_words) - (Math.floor(not_found_words / 2) + 1 if skipped_words else 0)
            total_words_halved = Math.ceil(total_words / 2)
            found_words -= skipped_words
            
            if found_words >= total_words_halved: # 50%+ Words Matched
                if multi_level_key > -1:
                    high_probability_list.append(game)
                else:
                    high_probability_list.append(game_title)
    
    return full_matched_list, high_probability_list


### Check for numbers and if found, switch to an alternate numbering system. Only for numbers 1-20 or I-XX.
### Note: This only goes one way; so if a Roman numeral is found it will no longer check for Arabic numerals.
###     (search_words) A string of search words.
###     (to_roman_numerals_only) "Only" check for Arabic numerals and change them to Roman numerals (2 -> II).
###     --> Returns a [str]
def changeNumberSystemIn(search_words: str, to_roman_numerals_only: bool = False) -> str:
    if to_roman_numerals_only:
        re_object = re_arabic_numerals
        search_numbers = arabic_numerals_list
        replacement_numbers = roman_numerals_list
    else:
        if uppercase_roman_numerals_only:
            re_object = RE_ROMAN_NUMERALS
        else:
            re_object = re_roman_numerals
        search_numbers = roman_numerals_list
        replacement_numbers = arabic_numerals_list
    
    all_n_found = []
    if uppercase_roman_numerals_only:
        all_n_found = re_object.findall(search_item)
        alt_search_words = search_words
    else:
        all_n_found = re_object.findall(search_item.lower())
        alt_search_words = search_words.lower()
    
    if len(all_n_found):
        for found_number in all_n_found:
            n = -1
            for number in search_numbers:
                n += 1
                if found_number == number:
                    alt_search_words = re_object.sub(rf'{replacement_numbers[n]}', alt_search_words, count=1)
                    break
    
    if alt_search_words.lower() == search_words.lower():
        if to_roman_numerals_only:
            return ''
        else: # If no Roman numerals found check for Arabic numerals now.
            return changeNumberSystemIn(search_words, True)
    else:
        return alt_search_words


### Create a XML file for saving user settings and choices made on each game disc.
###     --> Returns a [bool] Success or Failure
def createSettingsFile() -> bool:
    try:
        root = ET.Element('Data')
        tree = ET.ElementTree(root)
        element_settings = ET.SubElement(root, 'Settings')
        ET.indent(tree, space='  ', level=0) # Indent the tree for "pretty printing" (3.9+)
        tree.write(settings_file, encoding='utf-8', xml_declaration=True)
        return True
    except IOError as e:
        print(f"ERROR: Failed writing to XML file: {e}")
    except OSError as e:
        print(f"ERROR: Operating system error: {e}")
    except Exception as e:
        print(f'ERROR: {e}')
    return False


### Load settings from XML settings file.
###     --> Returns a [bool] Success or Failure
def loadSettings() -> bool:
    root = 0
    try:
        tree = ET.parse(settings_file)
        root = tree.getroot()
    except IOError as e:
        print(f"ERROR: Failed loading of XML file: {e}")
        print(f'ERROR: Failed to load settings from "{settings_file.name}"')
        return False
    except OSError as e:
        print(f"ERROR: Operating system error: {e}")
        print(f'ERROR: Failed to load settings from "{settings_file.name}"')
        return False
    except Exception as e:
        print(f'ERROR: {e}')
        print(f'ERROR: Failed to load settings from "{settings_file.name}"')
        return False
    
    element_launchbox_root = root.find('Settings/LaunchBox/Root')
    if element_launchbox_root is not None:
        updateSetting(LAUNCHBOX_ROOT, element_launchbox_root.text, False)
    else: # Settings file just created, but default root paths are correct and working.
        updatePathsUsing(LAUNCHBOX_ROOT)
    
    element_launchbox_type = root.find('Settings/LaunchBox/MediaType')
    if element_launchbox_type is not None:
        updateSetting(LAUNCHBOX_MEDIA_TYPE, element_launchbox_type.text, False)
    
    element_launchbox_search = root.find('Settings/LaunchBox/SearchBothNS')
    if element_launchbox_search is not None:
        updateSetting(SEARCH_BOTH_NUMBER_SYSTEMS, element_launchbox_search.text, False)
    
    element_launchbox_last_dir = root.find('Settings/LaunchBox/LastPS2Directory')
    if element_launchbox_last_dir is not None:
        updateSetting(LAST_PS2_DIRECTORY, element_launchbox_last_dir.text, False)
    
    element_pcsx2_root = root.find('Settings/PCSX2/Root')
    if element_pcsx2_root is not None:
        updateSetting(PCSX2_ROOT, element_pcsx2_root.text, False)
    else: # Settings file just created, but default root paths are correct and working.
        updatePathsUsing(PCSX2_ROOT)
    
    element_pcsx2_size = root.find('Settings/PCSX2/ImageSize')
    if element_pcsx2_size is not None:
        updateSetting(RESIZE_COVER_IMAGE, element_pcsx2_size.text, False)
    
    element_pcsx2_overwrite = root.find('Settings/PCSX2/Overwrite')
    if element_pcsx2_overwrite is not None:
        updateSetting(ALWAYS_OVERWRITE, element_pcsx2_overwrite.text, False)
    
    print('\n[Settings Loaded]')
    return True


### Set all settings back to their defaults.
def defaultSettings():
    root_path = rf'{ENV.get("ProgramFiles")}\LaunchBox'
    if Path(root_path).exists():
        updateSetting(LAUNCHBOX_ROOT, root_path, False)
    root_path = rf'{ENV.get("ProgramFiles")}\PCSX2'
    if Path(root_path).exists():
        updateSetting(PCSX2_ROOT, root_path, False)
    updateSetting(LAUNCHBOX_MEDIA_TYPE, 'Box - Front', False)
    updateSetting(SEARCH_BOTH_NUMBER_SYSTEMS, True, False)
    updateSetting(LAST_PS2_DIRECTORY, ROOT, False)
    updateSetting(RESIZE_COVER_IMAGE, 720, False)
    updateSetting(ALWAYS_OVERWRITE, True, True)


### Update and save a setting's value.
###     (setting) The setting constant.
###     (value) The setting value to change.
###     (save) Save settings to file.
###     (show_message) Show successful update messages.
###     --> Returns a [bool] Success or Failure
def updateSetting(setting: int, value, save: bool, show_message = True) -> bool:
    global launchbox_root
    global pcsx2_root
    global launchbox_media_type
    global resize_cover_image
    global always_overwrite
    global search_both_number_systems
    global launchbox_image_folder
    global last_ps2_directory
    
    # Update the setting varible
    if setting == LAUNCHBOX_ROOT:
        launchbox_root = str(value)
        updatePathsUsing(LAUNCHBOX_ROOT)
    
    elif setting == PCSX2_ROOT:
        pcsx2_root = str(value)
        updatePathsUsing(PCSX2_ROOT)
    
    elif setting == LAUNCHBOX_MEDIA_TYPE:
        launchbox_media_type = str(value)
        # If media types and paths loaded in, update "launchbox_image_folder" too.
        i = getListIndexOf(launchbox_media_type, launchbox_media_type_list, TYPE)
        if len(launchbox_media_type_list) > i > -1:
            launchbox_image_folder = launchbox_media_type_list[i][PATH]
    
    elif setting == RESIZE_COVER_IMAGE:
        resize_cover_image = int(value)
    
    elif setting == ALWAYS_OVERWRITE:
        always_overwrite = (str(value).lower() == "true")
    
    elif setting == SEARCH_BOTH_NUMBER_SYSTEMS:
        search_both_number_systems = (str(value).lower() == "true")
    
    elif setting == LAST_PS2_DIRECTORY:
        last_ps2_directory = str(value)
    
    else:
        print('\nWARNING: Setting Not Found!')
        return False
    
    if save:
        if show_message:
            print('\n[Settings Updated]')
        
        # Save changes to XML settings file
        try:
            tree = ET.parse(settings_file)
            root = tree.getroot()
            
            element_settings = root.find('Settings')
            
            element_launchbox = element_settings.find('LaunchBox')
            if element_launchbox is None:
                element_launchbox = ET.SubElement(element_settings, 'LaunchBox')
            
            element_pcsx2 = element_settings.find('PCSX2')
            if element_pcsx2 is None:
                element_pcsx2 = ET.SubElement(element_settings, 'PCSX2')
            
            element_launchbox_root = element_launchbox.find('Root')
            if element_launchbox_root is None:
                element_launchbox_root = ET.SubElement(element_launchbox, 'Root')
            element_launchbox_root.text = launchbox_root
            
            element_launchbox_type = element_launchbox.find('MediaType')
            if element_launchbox_type is None:
                element_launchbox_type = ET.SubElement(element_launchbox, 'MediaType')
            element_launchbox_type.text = launchbox_media_type
            
            element_launchbox_search = element_launchbox.find('SearchBothNS')
            if element_launchbox_search is None:
                element_launchbox_search = ET.SubElement(element_launchbox, 'SearchBothNS')
            element_launchbox_search.text = str(search_both_number_systems)
            
            element_launchbox_last_dir = element_launchbox.find('LastPS2Directory')
            if element_launchbox_last_dir is None:
                element_launchbox_last_dir = ET.SubElement(element_launchbox, 'LastPS2Directory')
            element_launchbox_last_dir.text = str(last_ps2_directory)
            
            element_pcsx2_root = element_pcsx2.find('Root')
            if element_pcsx2_root is None:
                element_pcsx2_root = ET.SubElement(element_pcsx2, 'Root')
            element_pcsx2_root.text = pcsx2_root
            
            element_pcsx2_size = element_pcsx2.find('ImageSize')
            if element_pcsx2_size is None:
                element_pcsx2_size = ET.SubElement(element_pcsx2, 'ImageSize')
            element_pcsx2_size.text = str(resize_cover_image)
            
            element_pcsx2_overwrite = element_pcsx2.find('Overwrite')
            if element_pcsx2_overwrite is None:
                element_pcsx2_overwrite = ET.SubElement(element_pcsx2, 'Overwrite')
            element_pcsx2_overwrite.text = str(always_overwrite)
            
            tree = ET.ElementTree(root)
            ET.indent(tree, space='  ', level=0)
            tree.write(settings_file, encoding='utf-8', xml_declaration=True)
            
            if show_message:
                print('[Settings Saved]')
            return True
        
        except IOError as e:
            print(f"ERROR: Failed writing to XML file: {e}")
        except OSError as e:
            print(f"ERROR: Operating system error: {e}")
        except Exception as e:
            print(f'ERROR: {e}')
        
        print(f'ERROR: Failed to save settings to "{settings_file.name}"')
        return False
    else:
        return True


### Show the settings menu and allow user to change and save each setting.
def showSettingsMenu():
    choices = [
        f'LaunchBox Root Directory\n        Current: {launchbox_root}\n',
        f'PCSX2 Root Directory\n        Current: {pcsx2_root}\n',
        f'LaunchBox Image Category\n        Current: {launchbox_media_type}\n',
        f'PCSX2 Cover Image Resize\n        Current: {resize_cover_image}\n',
        f'Always Overwrite PCSX2 Cover Image\n        Current: {always_overwrite}\n',
        f'Search For Both Arabic and Roman Numerals\n        Current: {search_both_number_systems}\n',
        f'Restore All Setting Defaults\n\n'
    ]
    setting_selection = selectionMenu(
        [f'\n{SCRIPT_TITLE} Settings:',
         f'(Choose which setting to change)\n'],
        choices,
        '--No More Changes--'
    )
    if setting_selection:
        print()
        setting_selection = setting_selection - 1
        setting = RE.sub(r'^(.*?)(\n)(.*?)(\n)$', r'\1', choices[setting_selection])
        
        if setting_selection == LAUNCHBOX_ROOT or setting_selection == PCSX2_ROOT:
            directory_path = selectDirectoryFor(setting_selection)
            if len(str(directory_path)) > 1 and Path(directory_path).exists():
                updateSetting(setting_selection, directory_path, True)
            else:
                print(f'\nWARNING: This path "{directory_path}" does not exist.')
        
        elif setting_selection == LAUNCHBOX_MEDIA_TYPE:
            selection = selectionMenu(
                [f'Select a {setting}:'],
                [media_type[TYPE] for media_type in launchbox_media_type_list],
                '--No Change--', 3
            )
            if selection:
                updateSetting(setting_selection, launchbox_media_type_list[selection - 1][TYPE], True)
        
        elif setting_selection == ALWAYS_OVERWRITE or setting_selection == SEARCH_BOTH_NUMBER_SYSTEMS:
            toggle = [True, False]
            selection = selectionMenu(
                [f'Set {setting}:'],
                toggle,
                '--No Change--'
            )
            if selection:
                updateSetting(setting_selection, toggle[selection - 1], True)
        
        elif setting_selection == DEFAULT_SETTINGS:
            selection = selectionMenu(
                [f'Are you sure you want to "{setting}"?'],
                ['Yes', 'No']
            )
            if selection == 1:
                defaultSettings()
        
        else: # Numbers or Text
            updated_setting = input(rf'Enter New "{setting}": ')
            
            if setting_selection == RESIZE_COVER_IMAGE:
                if updated_setting.isnumeric():
                    updateSetting(setting_selection, int(updated_setting), True)
                else:
                    print("\nWARNING: Invalid input, please enter only positive integers.")
        
        showSettingsMenu()
    else:
        # User not allowed to leave settings menu until root paths are correct.
        rootPathCheck() # -> showSettingsMenu()


### Update XML file after a new user choice made.
###     (game_title) The current LaunchBox game title.
###     (game_path) The current game disc path.
###     (choice) The string representing the choice being made.
###     (selection) The specific option selected from the choice given.
###     --> Returns a [bool] Success or Failure
def updateSavedChoice(game_title: str, game_path: str, choice: str, selection: int) -> bool:
    if settings_file.exists():
        tree = ET.parse(settings_file)
        root = tree.getroot()
        game_found = False
        path_found = False
        choice_updated = False
        
        for element_game in root.findall('Game'):
            element_game_title = element_game.find('Title')
            
            if element_game_title.text == game_title:
                game_found = True
                element_path = element_game.find(f'.//Disc[@path="{game_path}"]')
                
                if element_path is not None:
                    path_found = True
                    
                    if choice == 'Image' or choice == 'Overwrite':
                        element_choice = element_path.find(f'.//{choice}[@type="{launchbox_media_type}"]')
                    else:
                        element_choice = element_path.find(choice)
                    
                    if element_choice is not None:
                        element_choice.text = str(selection)
                        choice_updated = True
                break
        
        if not game_found:
            element_game = ET.SubElement(root, 'Game')
            element_game_title = ET.SubElement(element_game, 'Title')
            element_game_title.text = game_title
        
        if not path_found:
            element_path = ET.SubElement(element_game, 'Disc')
            element_path.set('path', game_path)
        
        if not choice_updated:
            element_choice = ET.SubElement(element_path, choice)
            
            if choice == 'Image' or choice == 'Overwrite':
                element_choice.set('type', launchbox_media_type)
            
            element_choice.text = str(selection)
            choice_updated = True
        
        if choice_updated:
            tree = ET.ElementTree(root)
            ET.indent(tree, space='  ', level=0)
            tree.write(settings_file, encoding='utf-8', xml_declaration=True)
            return True
    else:
        print(f'Failed to find and update "{settings_file.name}"')
    return False


### Remove a user choice from the XML file.
###     (game_title) The current LaunchBox game title.
###     (game_path) The current game disc path.
###     (choice) The string representing the choice being made.
###     --> Returns a [int] Selection
def removeSavedChoice(game_title: str, game_path: str, choice: str) -> bool:
    if settings_file.exists():
        tree = ET.parse(settings_file)
        root = tree.getroot()
        choice_removed = False
        
        for element_game in root.findall('Game'):
            element_game_title = element_game.find('Title')
            
            if element_game_title.text == game_title:
                element_path = element_game.find(f'.//Disc[@path="{game_path}"]')
                
                if element_path is not None:
                    
                    element_choice = None
                    if choice == 'Image' or choice == 'Overwrite':
                        element_choice = element_path.find(f'.//{choice}[@type="{launchbox_media_type}"]')
                    else:
                        element_choice = element_path.find(choice)
                    
                    if element_choice is not None:
                        element_path.remove(element_choice)
                        choice_removed = True
                break
        
        if choice_removed:
            tree = ET.ElementTree(root)
            ET.indent(tree, space='  ', level=0)
            tree.write(settings_file, encoding='utf-8', xml_declaration=True)
            return True
    else:
        print(f'Failed to find and update "{settings_file.name}"')
    return False


### Get a user selected choice from the XML file.
###     (game_title) The current LaunchBox game title.
###     (game_path) The current game disc path.
###     (choice) The string representing the choice being made.
###     --> Returns a [int] Selection
def getSavedChoice(game_title: str, game_path: str, choice: str) -> int:
    if settings_file.exists():
        tree = ET.parse(settings_file)
        root = tree.getroot()
        
        for element_game in root.findall('Game'):
            element_game_title = element_game.find('Title')
            
            if element_game_title.text == game_title:
                element_path = element_game.find(f'.//Disc[@path="{game_path}"]')
                
                if element_path is not None:
                    
                    element_choice = None
                    if choice == 'Image' or choice == 'Overwrite':
                        element_choice = element_path.find(f'.//{choice}[@type="{launchbox_media_type}"]')
                    else:
                        element_choice = element_path.find(choice)
                    
                    if element_choice is not None:
                        return int(element_choice.text)
                break
    return -1


### Open a dialog allowing user to select a directory for LaunchBox or PCSX2.
###     (app_dir) LAUNCHBOX_ROOT or PCSX2_ROOT.
###     --> Returns a [Path] to a Directory
def selectDirectoryFor(app_dir) -> Path:
    window = TK.Tk()  # Create a basic Tkinter window
    window.withdraw() # Hide the main window
    
    if app_dir == LAUNCHBOX_ROOT:
        start_dir = launchbox_root if Path(launchbox_root).exists() else ROOT
        
        file_path = FileDialog.askopenfilename( #askdirectory(
            title = f'Select The LaunchBox Application',
            initialdir = start_dir,
            filetypes = (('LaunchBox', 'LaunchBox.exe'), ('All files', '*.*'))
        )
    elif app_dir == PCSX2_ROOT:
        start_dir = pcsx2_root if Path(pcsx2_root).exists() else ROOT
        
        file_path = FileDialog.askopenfilename(
            title = f'Select The PCSX2 Application',
            initialdir = start_dir,
            filetypes = (('PCSX2', 'pcsx2*.exe'), ('All Files', '*.*'))
        )
    window.destroy() # Close the hidden window after the dialog is closed
    return Path(file_path).parent


### Open a dialog allowing user to select one or more PlayStation 2 discs.
###     --> Returns a [list] of Disc Paths
def selectPS2Discs() -> list:
    window = TK.Tk()  # Create a basic Tkinter window
    window.withdraw() # Hide the main window
    
    start_dir = last_ps2_directory if Path(last_ps2_directory).exists() else ROOT
    
    disc_paths = FileDialog.askopenfilenames(
        title = f'Select One or More PlayStation 2 Game Discs',
        initialdir = start_dir,
        filetypes = (('PS2 Discs', '*.bin *.chd *.cue *.iso'), ('All Files', '*.*'))
    )
    window.destroy() # Close the hidden window after the dialog is closed
    
    # Save last used PS2 games directory as a setting.
    if len(disc_paths):
        updateSetting(LAST_PS2_DIRECTORY, Path(disc_paths[0]).parent, True, False)
    
    return list(disc_paths)


### Print list of useful commands and other script details.
def printHelp():
    print('\nList of Useful Commands:')
    print('  [all]      Will create PCSX2 cover images for all LaunchBox games found.')
    print('  [open]     Will open a dialog window to manually find and select PS2 discs.')
    print('  [list =]   Will list or show all games found in =LaunchBox= or =PCSX2=.')
    print('  [show =]   Will open a file explorer pointing to the =LaunchBox= or =PCSX2= image directory.')
    print('  [settings] Will show all the changeable settings in this script.')
    print('\nOther Details:')
    print('  Type a "*" after any search to use the previous options already selected for any')
    print('  game title or disc found. Used to speed through back-and-forth image changes.')
    print('  Shorthand: LB = LaunchBox, PS = PCSX2, @ = Open, * = Settings, ? = Help')
    print('  The [show] command is usable at every input prompt.')
    print('  Leave the "--->" input prompt blank and press the "Enter" key to close this window.')


### Print out LaunchBox or PCSX2 PS2 game list.
###     (app) List games from "LaunchBox" or "PCSX2".
###     (show_id) Include the Game ID/Serial.
def printGames(app: str, show_id: bool = False):
    print()
    if app == 'LaunchBox':
        for game in launchbox_game_list:
            if show_id:
                print(f'Game ID:    {game[ID]}')
            print(f'Game Title: {game[TITLE]}')
            for disc_path in game[DISC_PATH]:
                print(f'Game Path:  {disc_path}')
            print()
    elif app == 'PCSX2':
        for game in pcsx2_user_game_list:
            if show_id:
                print(f'Game ID:    {game[ID]}')
            print(f'Game Title: {game[TITLE]}')
            print(f'Game Disc:  {game[DISC_PATH]}')
            print()


### Open a directory for user to see or make changes manually.
###     (directory_path) A path to a directory.
def openDirectory(directory_path: str):
    if directory_path == '.ALL' and len(launchbox_media_type_list):
        directory_path = str(Path(launchbox_media_type_list[0][PATH]).parent)
    platform = System.platform
    if platform == 'win32':
        Open(f'explorer "{directory_path}"')
    elif platform == 'linux':
        Open(['xdg-open', directory_path])
    elif platform == 'darwin': # macOS
        Open(['open', directory_path])
    else:
        print(f'WARNING: Failed to open directory. Operating system unknown or unsupported: "{os_platform}"')


### Prints a box pattern around one or more lines of text.
###     (text_lines) A list of text strings.
###     (box_pattern) A pattern of symbols to use as a border around the text.
###     (top_bottom_line_count) The amount of individual top and bottom lines to print.
###     (align) Alignment of the text inside the box pattern ("Left", "Center", "Right").
def showTitleBox(text_lines: list, box_pattern: str = '=', top_bottom_line_count: int = 1, align: str = 'Left'):
    # Get Lengths
    box_pattern_legnth = len(box_pattern)
    max_text_length = 0
    for text in text_lines:
        if len(text) > max_text_length:
            max_text_length = len(text)
    
    # Create top and bottom lines
    top_bottom_line = ''
    if box_pattern_legnth:
        add_more_length = 3
        if box_pattern_legnth == 1:
            add_more_length += 2
        elif box_pattern_legnth == 2:
            add_more_length += 1
        for i in range(0, Math.ceil((max_text_length / box_pattern_legnth)) + add_more_length):
            top_bottom_line += box_pattern
    
    # Create extra text aligning spaces if needed.
    spaces_added = len(top_bottom_line) - (max_text_length + box_pattern_legnth * 2)
    left_aligning_spaces = ''
    right_aligning_spaces = ''
    for i in range(0, spaces_added):
        if i == 0 and spaces_added % 2 == 1:
            # Add the odd extra space based on alignment.
            if align.lower() == 'right':
                left_aligning_spaces += ' '
            else:
                right_aligning_spaces += ' '
        elif i % 2 == 0:
            left_aligning_spaces += ' '
        else:
            right_aligning_spaces += ' '
    
    # Print Top Line(s)
    for i in range(0, top_bottom_line_count):
        print(top_bottom_line)
    
    # Print Center Line(s)
    for text in text_lines:
        extra_spaces = ''
        center_space = ''
        if len(text) < max_text_length: # Add extra spaces for shorter lines
            spaces_added = max_text_length - len(text)
            for i in range(0, Math.floor((spaces_added) / (2 if align == 'Center' else 1))):
                extra_spaces += ' '
            if spaces_added % 2 == 1:
                center_space += ' '
        if align.lower() == 'center':
            text = f'{box_pattern}{left_aligning_spaces}{extra_spaces}{text}{extra_spaces}{center_space}{right_aligning_spaces}{box_pattern}'
        elif align.lower() == 'right':
            text = f'{box_pattern}{left_aligning_spaces}{extra_spaces}{text}{right_aligning_spaces}{box_pattern}'
        else:
            text = f'{box_pattern}{left_aligning_spaces}{text}{extra_spaces}{right_aligning_spaces}{box_pattern}'
        print(text)
    
    # Print Bottom Line(s)
    for i in range(0, top_bottom_line_count):
        print(top_bottom_line)


### Script Starts Here
if __name__ == '__main__':
    print(f'Python v{System.version} [{System.platform}]')
    showTitleBox([SCRIPT_TITLE, SCRIPT_VERSION, SCRIPT_CREATOR], '|\__/|', 2, 'Right')
    MIN_VERSION = (3,9,0)
    MIN_VERSION_STR = '.'.join([str(n) for n in MIN_VERSION])
    assert System.version_info >= MIN_VERSION, f'This Script Requires Python v{MIN_VERSION_STR} or Newer'
    
    starting_message = True
    error = False
    loop = True
    use_saved_selections = always_use_previous_choices
    search_item = None # This could be a String or a Path
    all_games_search = False
    single_title_search = False
    multiple_disc_selections = []
    divider = '\n--------------------------------------------------\n'
    
    # Load or create saved user settings and choices from XML file.
    if settings_file.exists():
        loadSettings()
        rootPathCheck()
    else:
        createSettingsFile()
        if rootPathCheck():
            updatePathsUsing(LAUNCHBOX_ROOT)
            updatePathsUsing(PCSX2_ROOT)
    
    # Quick (Multi) Disc Drop
    if System.argv[1:] != []:
        multiple_disc_selections = System.argv[1:]
    
    ## Quick Testing
    #single_title_search = True
    #search_item = r''
    #multiple_disc_selections = [r'', r'']
    
    # Script Loop
    while loop:
        if search_item:
            game_list = []
            full_matched_game_list = []
            high_probability_game_list = []
            
            # Find Game Title(s)
            if all_games_search: # All Games, All Discs Search
                game_list = launchbox_game_list
            
            elif single_title_search: # Game Title Search (Multi-Disc)
                print(divider)
                selection = 0
                search_item = str(search_item)
                alt_search_item = ''
                
                if search_both_number_systems:
                    # Check for numbers and if found, combine two search results using different numbering systems. (2 <-> II)
                    alt_search_item = changeNumberSystemIn(search_item)
                
                # Preform the search (and also an extra alt search if needed).
                full_matched_game_list, high_probability_game_list = searchFor(search_item, launchbox_game_list, TITLE)
                if len(alt_search_item):
                    full_matched_game_list_alt, high_probability_game_list_alt = searchFor(alt_search_item, launchbox_game_list, TITLE)
                    # Merge the lists, no repeats/duplicates
                    for game in full_matched_game_list_alt:
                        if game not in full_matched_game_list:
                            full_matched_game_list.append(game)
                    for game in high_probability_game_list_alt:
                        if game not in full_matched_game_list and game not in high_probability_game_list:
                            high_probability_game_list.append(game)
                
                # Auto-select the only full match found or ask for the proper title if more than one.
                if len(full_matched_game_list) == 1:
                    game_list.append(full_matched_game_list[selection])
                else:
                    if len(full_matched_game_list) or len(high_probability_game_list):
                        if len(full_matched_game_list) > 1:
                            selection = selectionMenu(
                                ['Closely matched LaunchBox game titles found. Select the title you\'re looking for:'],
                                [game[TITLE] for game in full_matched_game_list],
                                '-- None Of The Above Match... Expand Search? --',
                                2 if len(full_matched_game_list) > 10 else 1
                            )
                        if selection == 0:
                            if len(high_probability_game_list):
                                if len(full_matched_game_list) > 1:
                                    print()
                                selection = selectionMenu(
                                    ['Loosely matched LaunchBox game titles found. Select the title you\'re looking for:'],
                                    [game[TITLE] for game in high_probability_game_list],
                                    '-- None Of The Above Match... Skip and Search For Another Game? --',
                                    2 if len(high_probability_game_list) > 10 else 1
                                )
                            if selection > 0:
                                game_list.append(high_probability_game_list[selection - 1])
                                print(divider)
                            else:
                                print()
                        else:
                            game_list.append(full_matched_game_list[selection - 1])
                            print(divider)
            
            else: # Single Disc Path Search
                print(divider)
                for game in launchbox_game_list:
                    for disc_path in game[DISC_PATH]:
                        if str(search_item) == disc_path:
                            game_list.append([ game[ID], game[TITLE], [disc_path] ])
            
            if len(game_list) == 0:
                print(f'No PS2 Games Found In LaunchBox For: {str(search_item)}')
            
            for game in game_list:
                
                if all_games_search:
                    print(divider)
                
                print(f'LaunchBox Title Found:')
                print(f'  {game[TITLE]}')
                for disc_path in game[DISC_PATH]:
                    print(f'    {disc_path}')
                
                for disc_path in game[DISC_PATH]:
                    
                    pcsx2_game_title_list = []
                    canceled = False
                    image_copied = False
                    image_resized = False
                    overwritten = False
                    
                    # Get PCSX2 game title using a disc path.
                    pcsx2_game_title = getPCSX2GameTitleFrom(disc_path, DISC_PATH)
                    if len(pcsx2_game_title): # Exact match has been made
                        pcsx2_game_title_list.append(pcsx2_game_title)
                    
                    # If for whatever reason a game disc match between LaunchBox and PCSX2 fails,
                    # fallback to a title search that allows user to select the correct title.
                    else:
                        selection = 0
                        search_item = game[TITLE]
                        alt_search_item = ''
                        
                        if search_both_number_systems:
                            # Check for numbers and if found, combine two search results using different numbering systems. (2 <-> II)
                            alt_search_item = changeNumberSystemIn(search_item)
                        
                        # Preform the search (and also an extra alt search if needed).
                        full_matched_game_list, high_probability_game_list = searchFor(search_item, pcsx2_full_game_list)
                        if len(alt_search_item):
                            full_matched_game_list_alt, high_probability_game_list_alt = searchFor(alt_search_item, pcsx2_full_game_list)
                            # Merge the lists, no repeats/duplicates
                            for found_game in full_matched_game_list_alt:
                                if found_game not in full_matched_game_list:
                                    full_matched_game_list.append(found_game)
                            for found_game in high_probability_game_list_alt:
                                if found_game not in full_matched_game_list and found_game not in high_probability_game_list:
                                    high_probability_game_list.append(found_game)
                        
                        # Auto-select the only full match found or ask for the proper title if more than one.
                        if len(full_matched_game_list) == 1:
                            pcsx2_game_title_list.append(full_matched_game_list[selection])
                        else:
                            
                            use_previous_selection = use_saved_selections
                            
                            if use_previous_selection:
                                saved_selection_full = getSavedChoice(game[TITLE], disc_path, 'FullMatched') - 1
                                saved_selection_loose = getSavedChoice(game[TITLE], disc_path, 'LooseMatched') - 1
                                
                                if len(full_matched_game_list) > saved_selection_full > -1:
                                    pcsx2_game_title_list.append(full_matched_game_list[saved_selection_full])
                                elif len(high_probability_game_list) > saved_selection_loose > -1:
                                    pcsx2_game_title_list.append(high_probability_game_list[saved_selection_loose])
                                else:
                                    use_previous_selection = False
                            
                            if not use_previous_selection:
                                
                                if len(full_matched_game_list) > 1:
                                    print(f'\nLaunchBox Title Found:')
                                    print(f'  {game[TITLE]}')
                                    print(f'    {disc_path}')
                                    selection = selectionMenu(
                                        ['\nMultiple very similarly matched titles found in the search results.',
                                         f'Try to match one of these PCSX2 titles with the LaunchBox game title and path above.'],
                                        full_matched_game_list,
                                        '-- None Of The Above Match... Expand Search? --',
                                        2 if len(full_matched_game_list) > 10 else 1
                                    )
                                    updateSavedChoice(game[TITLE], disc_path, 'FullMatched', selection)
                                
                                if selection == 0:
                                    if len(high_probability_game_list):
                                        print(f'\nLaunchBox Title Found:')
                                        print(f'  {game[TITLE]}')
                                        print(f'    {disc_path}')
                                        selection = selectionMenu(
                                            ['\nNo matching titles found, but here are some loosely matched search results.',
                                             f'Try to match one of these PCSX2 titles with the LaunchBox game title and path above.'],
                                            high_probability_game_list,
                                            '-- None Of The Above Match... Skip and Search For Another Game? --',
                                            2 if len(high_probability_game_list) > 10 else 1
                                        )
                                        if selection:
                                            updateSavedChoice(game[TITLE], disc_path, 'LooseMatched', selection)
                                    
                                    if selection == 0:
                                        print(f'\nNo Matching PCSX2 Titles Found For:')
                                        print(f'  {game[TITLE]}')
                                        print(f'    {disc_path}')
                                        continue
                                    else:
                                        pcsx2_game_title_list.append(high_probability_game_list[selection - 1])
                                else:
                                    pcsx2_game_title_list.append(full_matched_game_list[selection - 1])
                    
                    print(f'\nMatching PCSX2 Title Found:')
                    for pcsx2_game_title in pcsx2_game_title_list:
                        print(f'  {pcsx2_game_title}')
                    
                    # Find all reletive matching LaunchBox image files
                    image_list = []
                    image_search_query = game[TITLE].replace(':', '_').replace('\'', '_').replace('\\\\', '_').replace('\\', '_').replace('//', '_').replace('/', '_')
                    if launchbox_media_type == MEDIA_TYPE_ALL:
                        for lb_media_type, lb_image_dir in launchbox_media_type_list:
                            lb_image_dir = Path(lb_image_dir)
                            if lb_image_dir.exists():
                                for lb_image_path in lb_image_dir.rglob('*'): # Recursive Search
                                    if lb_image_path.is_file() and lb_image_path.suffix.lower() in supported_images:
                                        if getIndexOf(image_search_query, lb_image_path.stem) > -1:
                                            image_list.append(lb_image_path)
                    else:
                        for lb_image_path in Path(launchbox_image_folder).rglob('*'): # Recursive Search
                            if lb_image_path.is_file() and lb_image_path.suffix.lower() in supported_images:
                                if getIndexOf(image_search_query, lb_image_path.stem) > -1:
                                    image_list.append(lb_image_path)
                    images_found = len(image_list)
                    
                    if (images_found > 0):
                        selection = 1 # 0 index
                        
                        # Select the cover image to copy over if more than one found.
                        if (images_found > 1):
                            
                            use_previous_selection = use_saved_selections
                            
                            if use_previous_selection:
                                saved_selection_image = getSavedChoice(game[TITLE], disc_path, 'Image')
                                
                                if len(image_list) >= saved_selection_image > 0:
                                    selection = saved_selection_image
                                else:
                                    use_previous_selection = False
                            
                            if not use_previous_selection:
                                selection = selectionMenu(
                                    ['\nMultiple images found, choose which image file to copy to the PCSX2 cover folder.'],
                                    image_list, 'Cancel/Skip'
                                )
                                if selection:
                                    updateSavedChoice(game[TITLE], disc_path, 'Image', selection)
                                else:
                                    canceled = True
                        
                        if not canceled:
                            for pcsx2_game_title in pcsx2_game_title_list:
                                
                                source_image = image_list[selection - 1]
                                
                                # Create a new destination/save path
                                new_image_file_name = pcsx2_game_title.replace(':', ' -') + source_image.suffix
                                destination_image = pcsx2_image_folder / new_image_file_name
                                
                                print(f'\nLaunchBox Image Found:')
                                print(f'  Source Path:      {str(source_image)}')
                                print(f'  Destination Path: {str(destination_image)}')
                                
                                # Get all existing images with the same name minus extension. Only one image can be shown per game in PCSX2,
                                # but multple images can have the same game title with different extensions.
                                existing_images = []
                                destination_directory = destination_image.parent
                                for file in destination_directory.glob('*'):
                                    if file.is_file() and file.suffix.lower() in supported_images:
                                        if file.stem == destination_image.stem:
                                            existing_images.append(file)
                                
                                if len(existing_images):
                                    use_previous_selection = use_saved_selections
                                    selection = 0
                                    
                                    if use_previous_selection:
                                        saved_selection_image = getSavedChoice(game[TITLE], disc_path, 'Overwrite')
                                        if saved_selection_image == 1:
                                            selection = saved_selection_image
                                        else:
                                            use_previous_selection = False
                                    
                                    if not use_previous_selection:
                                        if always_overwrite:
                                            selection = 1
                                        else:
                                            selection = selectionMenu(
                                                ['\nAn image file of the same name already exists here. How do you wish to proceed.'],
                                                ['Overwrite', 'Rename'], 'Cancel/Skip'
                                            )
                                            if selection == 1:
                                                updateSavedChoice(game[TITLE], disc_path, 'Overwrite', selection)
                                            else:
                                                # Only the "Overwrite" option can be saved and reused.
                                                # If another option is selected, remove previous choice.
                                                removeSavedChoice(game[TITLE], disc_path, 'Overwrite')
                                    
                                    # Temporally rename existing file that will later be deleted/overwritten
                                    # (or reverted back to original name depending on successful file copy).
                                    if selection == 1:
                                        overwritten = True
                                        if destination_image in existing_images:
                                            temp_existing_image = pcsx2_image_folder / f'{new_image_file_name}.tmp'
                                            n = 0
                                            while temp_existing_image.exists():
                                                n += 1
                                                temp_existing_image = pcsx2_image_folder / f'{new_image_file_name}.tmp{n}'
                                            destination_image.rename(temp_existing_image)
                                            
                                            # Remove the new image from "existing_images" and add the temp file to be later deleted/overwritten.
                                            i = existing_images.index(destination_image)
                                            if i > -1:
                                                existing_images.pop(i)
                                            existing_images.append(temp_existing_image)
                                    
                                    # Rename cover image file... again.
                                    elif selection == 2:
                                        new_cover_image_name = ''
                                        while new_cover_image_name == '' or new_cover_image_name == destination_image.stem:
                                            new_cover_image_name = input(f'\nEnter the new cover image name (previous name = "{destination_image.stem}" ): ')
                                        new_image_file_name = new_cover_image_name + source_image.suffix
                                        destination_image = pcsx2_image_folder / new_image_file_name
                                        if destination_image.exists():
                                            continue # Try Again
                                    
                                    # Cancel copying and skip this game disc.
                                    elif selection == 0:
                                        canceled = True
                                
                                if canceled:
                                    print('\nCanceled!')
                                    canceled = False
                                else:
                                    # Copy (and if set, resize) a new cover image to a new location.
                                    if resize_cover_image > 0:
                                        print()
                                        image_copied = image_resized = resizeCoverImage(source_image, resize_cover_image, destination_image)
                                    
                                    # If image resizing din't happen for whatever reason, just copy the image to new location.
                                    if not image_copied:
                                        try:
                                            CopyFile(str(source_image), str(destination_image))
                                            image_copied = True
                                        except FileNotFoundError:
                                            print(f'\nERROR: Source image "{source_file}" not found.')
                                        except PermissionError:
                                            print(f'\nERROR: Permission denied when copying "{source_file}" to "{destination_file}".')
                                        except shutil.SameFileError:
                                            print(f'\nERROR: Source and destination images are the same: "{source_file}".')
                                        except Exception as e:
                                            print(f'\nERROR: Failed copying: "{source_file}" to "{destination_file}"\nAn unexpected error occurred: {e}')
                                    
                                    if image_copied:
                                        print(f'\nLaunchBox Image:\n  "{str(source_image)}"')
                                        if image_resized:
                                            print(f'Copied and Resized Successfully To The PCSX2 Folder:')
                                        else:
                                            print(f'Copied Successfully To The PCSX2 Folder:')
                                        print(f'  "{str(destination_image)}"')
                                    
                                    # Delete renamed/overwritten temp file (and others in existing_images) if copy successful
                                    # (or revert the renamed temp file).
                                    if overwritten and image_copied:
                                        for deleted_image in existing_images:
                                            try:
                                                deleted_image.unlink() #missing_ok=True
                                            except PermissionError:
                                                print(f'ERROR: Permission denied while attempting to delete file: "{deleted_image}".')
                                            except IsADirectoryError:
                                                print(f'ERROR: "{deleted_image}" is a directory, not a file. Use rmdir() or shutil.rmtree().')
                                            except FileNotFoundError:
                                                print(f'ERROR: This file "{deleted_image}" not found.')
                                            except Exception as e:
                                                print(f'ERROR: Failed to delete file: "{deleted_image}"\nAn unexpected error occurred: {e}')
                                    elif overwritten:
                                        for image in existing_images:
                                            if '.tmp' in image.suffix:
                                                try:
                                                    image.rename(destination_image)
                                                except FileNotFoundError:
                                                    print(f'ERROR: The temp file "{image}" was not found.')
                                                except IsADirectoryError:
                                                    print(f'ERROR: Cannot rename a file to an existing directory: "{destination_image}".')
                                                except NotADirectoryError:
                                                    print(f'ERROR: Cannot rename a directory to an existing file: "{destination_image}".')
                                                except PermissionError:
                                                    print(f'ERROR: Permission denied. Unable to rename "{image}".')
                                                except OSError as e:
                                                    print(f'ERROR: Failed to rename file: "{image}"\nAn unexpected error occurred: {e}')
                    else:
                        print(f'\nNo Cover Images Found For The Game: {game[TITLE]}')
            
            search_item = None
            if len(multiple_disc_selections) == 0:
                print(divider[:-1])
        
        else:
            # One or more file paths found. Go through list one by one.
            if len(multiple_disc_selections):
                search_item = Path(multiple_disc_selections.pop(0).strip())
                try_again = False
            else:
                try_again = loop_script
                loop = loop_script
                use_saved_selections = False
                all_games_search = False
                single_title_search = False
            
            # Command Prompt:
            while try_again:
                if starting_message:
                    starting_message = False
                    print('\nTo start drop, paste, or type a path to a PlayStation 2 disc file into this prompt.')
                    print('You can also search for a game by entering it\'s full or partial title name.')
                    print('Type "help" for additional information and commands.')
                else:
                    print('\nSearch for another game?')
                
                user_input = input('\n--->')
                if user_input == '':
                    loop = False # Quit
                    break
                
                user_input = user_input.replace('"', '')
                
                # Check for one or more file paths
                multiple_disc_selections = RE.findall(r'\w\:\\.*?(?=\w\:\\|$)', user_input)
                
                # Commands
                if user_input.lower() == 'help' or user_input.lower() == '?':
                    printHelp()
                    continue
                elif user_input.lower() == 'list launchbox' or user_input.lower() == 'list lb':
                    printGames('LaunchBox')
                    continue
                elif user_input.lower() == 'list pcsx2' or user_input.lower() == 'list ps':
                    printGames('PCSX2')
                    continue
                elif user_input.lower() == 'settings' or user_input.lower() == '*':
                    showSettingsMenu()
                    continue
                elif user_input.lower() == 'show launchbox' or user_input.lower() == 'show lb':
                    openDirectory(launchbox_image_folder)
                    continue
                elif user_input.lower() == 'show pcsx2' or user_input.lower() == 'show ps':
                    openDirectory(pcsx2_image_folder)
                    continue
                
                # Check if a search will use previous user choices/selections.
                if user_input[-1:] == '*':
                    use_saved_selections = True
                    user_input = user_input[:-1]
                
                # Run The Search
                if user_input.lower() == 'all':
                    all_games_search = True
                    search_item = user_input
                    break
                elif user_input.lower() == 'open' or user_input.lower() == '@':
                    multiple_disc_selections = selectPS2Discs()
                    break
                elif len(multiple_disc_selections):
                    if not Path(multiple_disc_selections[0]).exists():
                        # If not a file path then run a title search.
                        multiple_disc_selections = []
                        single_title_search = True
                        search_item = user_input
                    break
                else:
                    single_title_search = True
                    search_item = user_input
                    break
