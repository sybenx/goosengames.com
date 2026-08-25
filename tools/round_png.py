#!/usr/bin/env python3
"""Round the corners of an 8-bit RGBA PNG, with a real alpha channel.

  python3 tools/round_png.py in.png out.png [radius_fraction]

Exists because the only rasteriser on hand (macOS qlmanage) flattens
transparency to white, so it cannot produce a rounded icon with transparent
corners — it renders them white, which shows as white nubs on a dark tab bar.
This masks the square render instead. Pure stdlib: no Pillow in this repo.
"""
import struct, sys, zlib


def read_png(path):
    d = open(path, "rb").read()
    assert d[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos, idat, hdr = 8, b"", None
    while pos < len(d):
        (n,) = struct.unpack(">I", d[pos:pos+4])
        typ = d[pos+4:pos+8]
        data = d[pos+8:pos+8+n]
        if typ == b"IHDR":
            hdr = struct.unpack(">IIBBBBB", data)
        elif typ == b"IDAT":
            idat += data
        pos += 12 + n
    w, h, depth, color, _, _, interlace = hdr
    assert (depth, color, interlace) == (8, 6, 0), f"want 8-bit RGBA, got {hdr}"

    raw = zlib.decompress(idat)
    stride, out, prev = w * 4, bytearray(), bytearray(w * 4)
    pos = 0
    for _ in range(h):
        f = raw[pos]; pos += 1
        line = bytearray(raw[pos:pos+stride]); pos += stride
        for i in range(stride):
            a = line[i-4] if i >= 4 else 0
            b = prev[i]
            c = prev[i-4] if i >= 4 else 0
            if f == 1:   line[i] = (line[i] + a) & 255
            elif f == 2: line[i] = (line[i] + b) & 255
            elif f == 3: line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        out += line
        prev = line
    return w, h, out


def write_png(path, w, h, px):
    raw = b"".join(b"\x00" + bytes(px[y*w*4:(y+1)*w*4]) for y in range(h))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
    open(path, "wb").write(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b""))


def coverage(x, y, w, h, r, ss=4):
    """Fraction of pixel (x,y) inside the rounded rect — supersampled, so the
    corners stay smooth at 16px where a hard test would look chewed."""
    hits = 0
    for sy in range(ss):
        py = y + (sy + 0.5) / ss
        for sx in range(ss):
            px = x + (sx + 0.5) / ss
            cx = r if px < r else (w - r if px > w - r else px)
            cy = r if py < r else (h - r if py > h - r else py)
            if (px - cx) ** 2 + (py - cy) ** 2 <= r * r:
                hits += 1
    return hits / (ss * ss)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    frac = float(sys.argv[3]) if len(sys.argv) > 3 else 0.22
    w, h, px = read_png(src)
    r = min(w, h) * frac
    for y in range(h):
        for x in range(w):
            c = coverage(x, y, w, h, r)
            if c < 1.0:
                i = (y * w + x) * 4 + 3
                px[i] = int(px[i] * c + 0.5)
    write_png(dst, w, h, px)
    print(f"  {dst}: {w}x{h}, corners rounded at {frac:.0%}")


if __name__ == "__main__":
    main()
