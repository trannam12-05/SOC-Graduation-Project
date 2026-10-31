"""Khôi phục dữ liệu base64 từ font console thật; không chỉnh sửa ảnh minh chứng.

Mỗi trang hiển thị bảng chữ cái ở hàng 0 và tối đa 18 dòng dữ liệu (80 ký tự).
Chỉ chấp nhận glyph khớp chính xác; SHA-256 tệp gốc phải đối chiếu riêng.
"""
import argparse
from pathlib import Path
import struct
import zlib

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='

def read_png(path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    offset = 8
    compressed = b''
    while offset < len(data):
        size = struct.unpack('>I',data[offset:offset+4])[0]
        kind = data[offset+4:offset+8]
        body = data[offset+8:offset+8+size]
        if kind == b'IHDR':
            width,height,depth,color,_,_,_ = struct.unpack('>IIBBBBB', body)
            assert depth == 8 and color == 2
        if kind == b'IDAT':
            compressed += body
        offset += size+12
    raw = zlib.decompress(compressed)
    rows = []
    for i in range(height):
        line = raw[i*(width*3+1):(i+1)*(width*3+1)]
        assert line[0] == 0
        rows.append(line[1:])
    return width,height,rows

def decode(path,length=1440):
    width,height,rows = read_png(path)
    assert width == 720 and height == 400
    def glyph(x,y):
        return bytes(1 if max(rows[r][c*3:c*3+3]) > 100 else 0
                     for r in range(y*16,(y+1)*16) for c in range(x*9,(x+1)*9))
    templates = {glyph(i,0):char for i,char in enumerate(ALPHABET)}
    assert len(templates) == len(ALPHABET), 'Bảng font không duy nhất hoặc sai vị trí'
    blank = bytes(144)
    output = ''
    for y in range(1,(length+79)//80+1):
        for x in range(min(80,length-(y-1)*80)):
            cell = glyph(x,y)
            if cell not in templates:
                raise ValueError(f'Glyph không khớp tại {x},{y}; không đoán ký tự')
            output += templates[cell]
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image',type=Path)
    args = parser.parse_args()
    print(decode(args.image))
