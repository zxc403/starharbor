import os, glob
from PIL import Image, ImageFilter, ImageStat

OUT = '/workspace/shots'
files = sorted(glob.glob(os.path.join(OUT, '*.jpg')))

def lum(p):
    return p[0]*0.299 + p[1]*0.587 + p[2]*0.114

for f in files:
    im = Image.open(f).convert('RGB')
    w, h = im.size
    px = im.load()
    # downsample for speed
    small = im.resize((160, 90))
    sp = small.load()
    sw, sh = small.size

    lums = []
    sats = []
    hues = set()
    for y in range(sh):
        for x in range(sw):
            r, g, b = sp[x, y]
            L = 0.299*r + 0.587*g + 0.114*b
            mx, mn = max(r,g,b), min(r,g,b)
            sat = (mx - mn) / max(1, mx) * 100
            lums.append(L)
            sats.append(sat)
            # quantized hue bucket
            if mx > 20:
                if mx - mn < 14:
                    hues.add('gray')
                else:
                    if mx == r: hues.add('R')
                    elif mx == g: hues.add('G')
                    else: hues.add('B')

    mean = sum(lums)/len(lums)
    var = sum((v-mean)**2 for v in lums)/len(lums)
    contrast = var**0.5
    sat_mean = sum(sats)/len(sats)

    # edge energy (Laplacian on luminance)
    g = im.convert('L').resize((320, 180))
    lap = g.filter(ImageFilter.FIND_EDGES)
    lp = lap.load()
    edge_sum = 0
    n = 0
    for y in range(180):
        for x in range(320):
            edge_sum += lp[x, y]
            n += 1
    edge_energy = edge_sum / n

    # sky ratio: top 40% avg lum vs bottom
    top = [lum(px[x, int(h*0.06)]) for x in range(0, w, max(1, w//200))]
    bot = [lum(px[x, int(h*0.85)]) for x in range(0, w, max(1, w//200))]
    top_m = sum(top)/len(top)
    bot_m = sum(bot)/len(bot)

    name = os.path.basename(f)
    print(f"{name:16s} {w}x{h}  lum={mean:5.1f}  contrast={contrast:5.1f}  sat={sat_mean:5.1f}  edge={edge_energy:6.1f}  sky/top={top_m:5.1f} bot={bot_m:5.1f}  hues={len(hues)}")
