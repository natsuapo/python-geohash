# coding: UTF-8
# Coder for Japanese grid square code. (JIS C 6304 / JIS X 0410)
# 行政管理庁告示第143号 http://www.stat.go.jp/data/mesh/

'''
1次メッシュコード: 緯度差は40分、経度差は1度となっている。1辺の長さは約80kmである。（4桁）
第2次メッシュ: 2桁の数字で、上1桁が緯度方向、下1桁が経度方向を表す。これに1次メッシュコードを合せて5339-23のように表す。1辺の長さは約10km
第3次メッシュ:2次メッシュコードと同様に2桁の数字で、上1桁が緯度方向、下1桁が経度方向を表す。これに1次・2次メッシュコードを合せて5339-23-43のように表す。1辺の長さは約1km
'''


from shapely.geometry import box

jp_box = [122,20,154,46]

def _encode_i2c(lat, lon, base1):
    # assert in_box(lat=lat,lon=lon,aoi=jp_box)  == True
    t = []
    while base1 > 80:
        if base1 == 800:
            t.append(lon % 10)
            t.append(lat % 10)
            lat = int(lat / 10)
            lon = int(lon / 10)
            base1 = int(base1 / 10)
        else:
            t.append(1 + (lat & 1) * 2 + (lon & 1))
            lat = lat >> 1
            lon = lon >> 1
            base1 = base1 >> 1

    if base1 == 80:
        t.append(lon % 10)
        t.append(lat % 10)
        lat = int(lat / 10)
        lon = int(lon / 10)
        base1 = int(base1 / 10)
    elif base1 == 16:  # Uni5
        t.append(1 + (lat & 1) * 2 + (lon & 1))
        lat = lat >> 1
        lon = lon >> 1
        base1 = base1 >> 1
    elif base1 == 40:  # Uni2
        t.append(5)
        t.append(lon % 5 * 2)
        t.append(lat % 5 * 2)
        lat = int(lat / 5)
        lon = int(lon / 5)
        base1 = int(base1 / 5)

    if base1 == 8:
        t.append(lon % 8)
        t.append(lat % 8)
        lat = lat >> 3
        lon = lon >> 3
        base1 = base1 >> 3

    t.append(lon)
    t.append(lat)
    t.reverse()
    return ''.join([str(i) for i in t])


def encode(latitude,longitude,base1=80):
    return _encode_i2c(int(latitude * base1 * 1.5), int(longitude * base1 - 100.0 * base1), base1)


# def _encode_i2c(lat, lon, base1):
def _decode_c2i(gridcode,div10=False):
    base1 = 1
    lat = lon = 0
    codelen = len(gridcode)
    if codelen > 0:
        lat = int(gridcode[0:2])
        lon = int(gridcode[2:4])

    if codelen > 4:
        lat = (lat << 3) + int(gridcode[4:5])
        lon = (lon << 3) + int(gridcode[5:6])
        base1 = base1 << 3

    if codelen > 6:
        if codelen == 7:
            i = int(gridcode[6:7]) - 1
            lat = (lat << 1) + int(i / 2)
            lon = (lon << 1) + i % 2
            base1 = base1 << 1
        else:
            lat = lat * 10 + int(gridcode[6:7])
            lon = lon * 10 + int(gridcode[7:8])
            base1 = base1 * 10

    if codelen > 8:
        if div10:
            lat = lat * 10 + int(gridcode[8:9])
            lon = lon * 10 + int(gridcode[9:10])
            base1 = base1 * 10
        else:
            if gridcode[8:] == '5':
                lat = lat >> 1
                lon = lon >> 1
                base1 = base1 >> 1
            else:
                for i in gridcode[8:]:
                    i = int(i) - 1
                    lat = (lat << 1) + int(i / 2)
                    lon = (lon << 1) + i % 2
                    base1 = base1 << 1

    return (lat, lon, base1)


def decode_sw(gridcode, delta=False,div10=False):
    (lat, lon, base1) = _decode_c2i(gridcode,div10=div10)

    lat = lat / (base1 * 1.5)
    lon = lon / float(base1) + 100.0

    if delta:
        return (lat, lon, 1.0 / (base1 * 1.5), 1.0 / base1)
    else:
        return (lat, lon)


def decode(gridcode,div10=False):
    gridcode = str(gridcode)

    (lat, lon, base1) = _decode_c2i(gridcode,div10)

        # center position of the meshcode.
    lat = (lat << 1) + 1
    lon = (lon << 1) + 1
    base1 = base1 << 1

    return (lat / (base1 * 1.5),lon / float(base1) + 100.0)



    # else:
    #     ### currently only support 100 meters
    #     if base1 == 800:
    #         grid_x = gridcode[-1]
    #         assert len(gridcode) == 10
    #         (a,b,c,d) = decode_sw(gridcode[:8],delta=True)
    #         return




def bbox(gridcode,div10=False):
    (a, b, c, d) = decode_sw(gridcode, True,div10=div10)
    return {'w': a, 's': b, 'n': b + d, 'e': a + c}

def bbox_shape(gridcode):
    try:
        (a, b, c, d) = decode_sw(gridcode, True)
        return box(b,a,b+d,a+c)
    except:
        return None

## short-cut methods
def encodeLv1(lat, lon):
    return encode(lat, lon, 1)


def encodeLv2(lat, lon):
    return encode(lat, lon, 8)


def encodeLv3(lat, lon):
    return encode(lat, lon, 80)


def encodeBase(lat, lon):
    return encodeLv3(lat, lon)


def encodeHalf(lat, lon):
    return encode(lat, lon, 160)


def encodeQuarter(lat, lon):
    return encode(lat, lon, 320)


def encodeEighth(lat, lon):
    return encode(lat, lon, 640)

def encodeUni100(lat,lon):
    return encode(lat,lon,800)

def encodeUni10(lat, lon):
    return encodeLv2(lat, lon)


def encodeUni5(lat, lon):
    return encode(lat, lon, 16)


def encodeUni2(lat, lon):
    return encode(lat, lon, 40)

def neighbors(gridcode):
    (lat, lon, base1) = _decode_c2i(gridcode)
    ret = []
    for i in ((0, -1), (0, 1), (1, -1), (1, 0), (1, 1), (-1, -1), (-1, 0), (-1, 1)):
        tlat = lat + i[0]
        tlon = lon + i[1]
        if tlat < 0 or tlat > (90 * base1):
            continue
        if tlon < 0 or tlon > (100 * base1):
            continue
        ret.append(_encode_i2c(tlat, tlon, base1))
    return ret

def expand(gridcode):
    ret = neighbors(gridcode)
    ret.append(gridcode)
    return ret

def multi_jp_grid(gridcode,step=1):
    assert type(gridcode) == str and len(gridcode)
    if step == 1:
        return str(gridcode)[0:4]
    elif step == 8:
        return str(gridcode)[0:6]
    elif step == 80:
        return str(gridcode)[0:8]
    
def neighboring_mesh_extract(mesh_code,fourdir=False,self_inc=True):
    lon,lat,base1 = _decode_c2i(mesh_code)
    if fourdir:
        range = [(-1, 0), (1, 0), (0, 1), (0, -1)]
    else:
        range = [(-1,-1),(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1)]
    if self_inc:
        range+= [(0,0)]
    return [_encode_i2c(lon+x,lat+y,base1) for x,y in range]

# def polygon_encode(step=1):
if __name__ == '__main__':
    print(encode(latitude=34.7359,longitude=139.0012,base1=800))



