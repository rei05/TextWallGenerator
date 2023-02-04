import os
import re
import numpy as np
import csv
import json
#from pykakasi import kakasi
from functions import *
import unicodedata
import yaml

#kakasi = kakasi() 
#kakasi.setMode("H", "a")
#kakasi.setMode("K", "a")
#kakasi.setMode("J", "a")
#kakasi.setMode("r", "Hepburn")
#conv = kakasi.getConverter()


def init_wall(x,y,w,h):
    wall = {'_time': 0, '_lineIndex': 0, '_type': 0, '_duration': 0, '_width': 0,
            '_customData': {'_position': [x,y], '_scale': [w,h,0.1], '_animation': {'_scale': [[1,1,1,0]]},
                            '_fake':True, '_interactable':False, "_noteJumpStartBeatOffset": 0}
            }
    return wall

def forced_centering(walls):
        x_list = np.array([wall['_customData']['_position'][0] for wall in walls['_obstacles']])
        w_list = np.array([wall['_customData']['_animation']['_scale'][0][0] for wall in walls['_obstacles']])
        x_offset = -(max(x_list+w_list) + min(x_list))/2
        for wall in walls['_obstacles']:
            wall['_customData']['_position'][0] += x_offset

def frameThick(walls, thicc):
    for wall in walls['_obstacles']:
        w = wall['_customData']['_animation']['_scale'][0][0]
        wall['_customData']['_scale'][0] *= 1/thicc
        wall['_customData']['_scale'][1] *= 1/thicc
        wall['_customData']['_scale'][2] *= 1/thicc
        wall['_customData']['_animation']['_scale'][0][0] *= thicc
        wall['_customData']['_animation']['_scale'][0][1] *= thicc
        wall['_customData']['_animation']['_scale'][0][2] *= thicc
        wall['_customData']['_position'][0] -= (1-1/thicc)/2

# scaleとanimatesacleを入れ替え
def x_adjust(walls):
    for wall in walls['_obstacles']:
        w,h,l = wall['_customData']['_scale']
        wall['_customData']['_animation']['_scale'][0] = [w,h,l,0]
        wall['_customData']['_scale'] = [1,1,1]
        wall['_customData']['_position'][0] += (w-1)/2

def setTime(walls,time):
    for wall in walls['_obstacles']:
        wall['_time'] = time

def setDuration(walls,duration):
    for wall in walls['_obstacles']:
        wall['_duration'] = duration

def setTrack(walls,trackName):
    for wall in walls['_obstacles']:
        wall['_customData']['_track'] = trackName

def setDissolve(walls):
    for wall in walls['_obstacles']:
        wall['_customData']['_animation']['_dissolve'] = [[0,0],[1,1e-9]]

def setDefinitePosition(walls):
    for wall in walls['_obstacles']:
        wall['_customData']['_animation']['_definitePosition'] = [[0,0,0,0]]

def centering(walls,fontDotSize):
    for wall in walls['_obstacles']:
        x,y = wall['_customData']['_position']
        x += 0.5-fontDotSize/2
        y += 0.5-fontDotSize/2
        wall['_customData']['_position'] = [x,y]

def resize(walls,charSize,fontDotSize):
    resizeRate = charSize/fontDotSize
    for wall in walls['_obstacles']:
        x,y = wall['_customData']['_position']
        w,h,l = wall['_customData']['_scale']
        x = (x+0.5-fontDotSize/2)*resizeRate
        y = (y+0.5-fontDotSize/2)*resizeRate
        w *= resizeRate
        h *= resizeRate
        wall['_customData']['_position'] = [x,y]
        wall['_customData']['_scale'] = [w,h,l]


def positionOffset(walls, size, length, char_shift, direction, isSmall, isHalf):
    for wall in walls['_obstacles']:
        x,y = wall['_customData']['_position']
        x += size
        y += size
        if direction=='h':
            x += char_shift - (length/2)*size - 0.1
            y += 0
            if isHalf:
                x += size*0.25
        elif direction=='v':
            x += (0.8-size/2)
            y -= char_shift + size - (length+1)*size
            if isSmall:
                y += size*0.2
        wall['_customData']['_position'] = [x,y]

def make_rotation_sw(walls,name,Angle,Direction,Duration,position,rotation,rotType):
    text = f'workspace: {name}\n'
    for wall in walls['_obstacles']:
        text += '\n0: RotationWall\n' if rotType == 1 else '\n0: RotationWall2\n'
        w,h,l = wall['_customData']['_scale']
        text += f'\tScale: [{w},{h},{l}]\n'
        x,y = wall['_customData']['_position']
        text += f'\tRadius: {x+w/2}\n'
        text += f'\tCenter: [{position[0]},{y+h/2+position[1]},{position[2]}]\n'
        text += f'\tAngle: {Angle}\n'
        text += f'\tDirection: {Direction}\n'
        text += f'\tDuration: {Duration}\n'
    text += '\n0: appendwalls\n'
    text += f'\tAnimateRotation: [{rotation[0]},{rotation[1]},{rotation[2]},0]\n'
    text += '\tappendtechnique: 0\n'
    return text


def charType(char):
    re_hiragana = re.compile(r'^[あ-ん]+$')
    if re_hiragana.fullmatch(char): return 'hira'
    re_katakana = re.compile(r'[\u30A1-\u30F4]+')
    if re_katakana.fullmatch(char): return 'kata'
    re_kanji = re.compile(r'^[\u4E00-\u9FD0]+$')
    if re_kanji.fullmatch(char): return 'kanji'
    return 'char'

def offsetCharSize(cType,size):
    if cType=='kanji':
        charSize = size*1.1
    elif cType=='hira':
        charSize = size*0.9
    else:
        charSize = size
    return charSize

#def jp2Roman(char):
#    result = conv.do(char)
#    if result=='\u300c': result = 'left'
#    if result=='\u300d': result = 'right'
#    if result=='/': result = 'slash'
#    return result

def isSmall(char):
    smallChars = ['っ','ゃ','ゅ','ょ','ぁ','ぃ','ぅ','ぇ','ぉ','ゎ']
    smallChars.extend(['ッ','ャ','ュ','ョ','ァ','ィ','ゥ','ェ','ォ','ヮ'])
    return (char in smallChars)

def isHalf(char):
    return 'Na' == unicodedata.east_asian_width(char)

def makeWall(char,font,n_dot):

    #文字を画像に変換
    img,fullwide = char2image(char,font)

    #画像を二値行列に変換
    matrix = image2matrix(img,fullwide,n_dot)

    #複合長方形領域に分割
    arrangement = div2rectangle(matrix,fullwide,n_dot)
    
    _obstacles = []
    for (x,y,w,h) in arrangement:
        wall = init_wall(x,y,w,h)
        _obstacles.append(wall)
    dat = {'_obstacles':_obstacles}
    return dat


def GetInputSettings(filename):
    try:
        with open(filename, encoding='shift_jis', newline='') as f:
            rows = [row for row in csv.reader(f)]
        setting_keys = rows[0]
        input_settings = [dict(zip(setting_keys, setting_values)) for setting_values in rows[1:]]           
        return input_settings
    except:
        print(f"[ERROR] {filename}の取得に失敗しました。")
        os.system('PAUSE'); exit()


if __name__ == '__main__':

    with open('settings.yaml') as f:
        env_settings = yaml.safe_load(f)

    input_settings = GetInputSettings('input.csv')

    customEvents = []

    os.makedirs("generated_files", exist_ok=True)

    for setting in input_settings:
        text       = setting["Text"]
        track_name = setting["TrackName"]
        t_start    = float(setting["StartBeatTime"])
        duration   = float(setting["Duration"]) - env_settings["HJD"]*2
        direction  = setting["Direction"]
        font       = "fonts/" + setting["Font"]
        dot_size   = int(setting["DotSize"])
        behavior   = setting["Behavior"]
        length     = len(text)
        size       = 1
        time       = t_start + env_settings["HJD"]
        
        charShift = 1
        obstacles = {"_obstacles":[]}
        child_tracks = []

        for i_char, char in enumerate(text):
            if char==' ': continue
            child_track_name = f'{track_name}_{i_char}'
            child_tracks.append(child_track_name)

            walls = makeWall(char,font,dot_size)
            ini_walls = walls.copy()

            centering(walls,dot_size)

            resize(walls,size,dot_size)

            #if isHalf(char) & (direction == "h"):
            #    charShift -= size*0.5
            #if isSmall(char): 
            #    if direction == "v":
            #        charShift -= size*0.3
            #    elif direction == "h":
            #        charShift -= size*0.15
            #    else:
            #        exit('ERROR: Direction設定が不正です。')

            positionOffset(walls, size, length, charShift, direction, isSmall(char), isHalf(char))
            setTrack(walls, child_track_name)
            setDuration(walls, duration)
            setTime(walls, time)
            if behavior=="stop":
                setDissolve(walls)
                setDefinitePosition(walls)

            x_adjust(walls)
            frameThick(walls, 12)

            #forced_centering(walls)

            obstacles["_obstacles"].extend(walls["_obstacles"])

            charShift += size

            if isSmall(char) & (direction != "v"):
                charShift -= size*0.15

        with open('generated_files/'+track_name+'.dat','w') as f:
            dat = json.dumps(obstacles["_obstacles"], indent=4)[6:-2].replace("\n    ","\n")
            f.write(dat)

        customEvents.append({'_time':0,'_type':'AssignTrackParent',
                             '_data':{'_parentTrack': track_name,
                                      '_childrenTracks': child_tracks}
                            })

    parentTracksData = {'_customData':{'_customEvents':customEvents}}
    with open('generated_files/parentTracks.dat','w') as f:
        dat = json.dumps(parentTracksData["_customData"]["_customEvents"], indent=4)[6:-2].replace("\n    ","\n")
        f.write(dat)

    print("Completed!")
    os.system('PAUSE')