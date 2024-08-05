from PIL import Image,ImageDraw,ImageFont
import numpy as np
import unicodedata

fontsize = 256 #フォントサイズ

#文字を画像に変換
def char2image(char, ttfontname):
    
    #全角/半角判定
    fullwide = unicodedata.east_asian_width(char) in 'FWA'
    canvasSize = (fontsize,fontsize) if fullwide else (int(fontsize/2),fontsize)

    # 文字を描く画像の作成
    img  = Image.new('RGB', canvasSize, (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 用意した画像に文字列を描く
    font = ImageFont.truetype(ttfontname, fontsize)
    textTopLeft = (0,0)
    draw.text(textTopLeft, char, fill=(0,0,0), font=font)

    return img,fullwide


def image2matrix(img,fullwide,n_dot):
    
    dotsize = fontsize/n_dot #ドットサイズ

    #全角/半角判定
    _n_dot = n_dot if fullwide else int(n_dot/2)
    
    matrix = []
    for iy in range(n_dot):
        row = []
        for ix in range(_n_dot):
            c_x = int(ix*dotsize+(dotsize/2))
            c_y = int(iy*dotsize+(dotsize/2))
            value = np.array(img)[c_y][c_x][0]
            row.append(1 if value<120 else 0)
        matrix.append(row)
        
    return matrix


def div2rectangle(matrix,fullwide,n_dot):
    
    #全角/半角判定
    _n_dot = n_dot if fullwide else int(n_dot/2)

    matrix = (np.array(matrix))
    arrangement = []
    while True:
        h_lines = []
        v_lines = []
        # Horizontal lines
        for i in range(n_dot):
            start_j = None
            for j in range(_n_dot):
                if matrix[i, j] and start_j is None:
                    start_j = j
                if not matrix[i, j] and start_j is not None:
                    h_lines.append((j - start_j, i, start_j))
                    start_j = None
            if start_j is not None:
                h_lines.append((_n_dot - start_j, i, start_j))
        # Vertical lines
        for j in range(_n_dot):
            start_i = None
            for i in range(n_dot):
                if matrix[i, j] and start_i is None:
                    start_i = i
                if not matrix[i, j] and start_i is not None:
                    v_lines.append((i - start_i, start_i, j))
                    start_i = None
            if start_i is not None:
                v_lines.append((n_dot - start_i, start_i, j))
        # Choose the longest line, add it and clear the pixels
        h_lines.sort(key=lambda x: x[0], reverse=True)
        v_lines.sort(key=lambda x: x[0], reverse=True)
        if not h_lines and not v_lines:
            break
        elif not h_lines or v_lines[0][0] >= h_lines[0][0]:
            h, i, j = v_lines[0]
            arrangement.append((j, n_dot - i - h, 1, h))
            for r in range(i, i + h):
                matrix[r, j] = False
        else:
            w, i, j = h_lines[0]
            arrangement.append((j, n_dot - i - 1, w, 1))
            for c in range(j, j + w):
                matrix[i, c] = False

    return arrangement
