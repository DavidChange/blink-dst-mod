"""Compilador minimo de builds de animacao do Don't Starve Together (sem Mod Tools).

Formato conferido byte a byte contra arquivos reais: builds compilados pelo autocompiler da
Klei e builds originais do jogo (swap_spear, torso_amulets). Gera:
  - build.bin (BILD v6): simbolos, quadros, vertices (2 triangulos por quadro) e tabela de nomes;
  - atlas-0.tex (KTEX DXT5, 2D, cadeia completa de mipmaps, alfa PRE-MULTIPLICADO como no jogo).
Coordenadas: unidades = pixels da imagem; y cresce para baixo; v da textura = 1 no topo.
Requer Pillow (com codificacao DDS/DXT5) e numpy.
"""
import io, struct, zipfile
import numpy as np
from PIL import Image

def klei_hash(text):
    h = 0
    for c in text.lower():
        h = (ord(c) + (h << 6) + (h << 16) - h) & 0xFFFFFFFF
    return h

def premultiply(im):
    a = np.array(im.convert('RGBA')).astype(np.float32)
    a[:, :, :3] *= a[:, :, 3:4] / 255.0
    return Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8), 'RGBA')

def _ktex_header(pixfmt, mips):
    return b'KTEX' + struct.pack('<I', (pixfmt << 4) | (1 << 9) | (mips << 13) | (3 << 18) | (4095 << 20))

def _mip_chain(im):
    chain = [im]
    while chain[-1].width > 1 or chain[-1].height > 1:
        w, h = max(1, chain[-1].width // 2), max(1, chain[-1].height // 2)
        chain.append(chain[-1].resize((w, h), Image.BOX))
    return chain

def _dxt5(im):
    w, h = im.size
    pad = Image.new('RGBA', (max(4, w), max(4, h)))
    pad.paste(im, (0, 0))
    buf = io.BytesIO()
    pad.save(buf, 'DDS', pixel_format='DXT5')
    data = buf.getvalue()[128:]
    expected = max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * 16
    assert len(data) == expected, (w, h, len(data), expected)
    return data

def ktex_dxt5(im):
    """Textura de animacao: pre-multiplica, inverte (armazenada de baixo para cima), DXT5 + mipmaps."""
    base = premultiply(im).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    chain = _mip_chain(base)
    heads, blobs = b'', b''
    for m in chain:
        data = _dxt5(m)
        pitch = max(1, (m.width + 3) // 4) * 16
        heads += struct.pack('<HHHI', m.width, m.height, pitch, len(data))
        blobs += data
    return _ktex_header(2, len(chain)) + heads + blobs

def ktex_rgba(im):
    """Textura de interface (atlas XML): RGBA sem compressao, 1 mip, alfa pre-multiplicado."""
    base = premultiply(im).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    raw = base.tobytes()
    w, h = base.size
    return _ktex_header(4, 1) + struct.pack('<HHHI', w, h, w * 4, len(raw)) + raw

def _pack(images, pad=4):
    """Empacotamento em prateleiras num quadrado potencia de 2."""
    order = sorted(range(len(images)), key=lambda i: -images[i].height)
    size = 64
    while True:
        pos, x, y, row = {}, pad, pad, 0
        ok = True
        for i in order:
            w, h = images[i].size
            if x + w + pad > size:
                x, y, row = pad, y + row + pad, 0
            if w + 2 * pad > size or y + h + pad > size:
                ok = False
                break
            pos[i] = (x, y)
            x += w + pad
            row = max(row, h)
        if ok:
            return size, pos
        size *= 2

def build_zip(path, build_name, symbols, anim_bin=None):
    """symbols: lista de (nome_do_simbolo, [(numero_do_quadro, duracao, imagem RGBA, (pivo_x, pivo_y) em px)]).
    Retorna o atlas (imagem) para conferencia."""
    # O jogo procura simbolos assumindo ordem crescente de hash (todos os builds originais sao
    # ordenados assim). Fora de ordem, simbolos "somem" no jogo (Dagger na agua 0.6.8/0.6.9, corpo 0.7.0).
    symbols = sorted(symbols, key=lambda s: klei_hash(s[0]))
    images = []
    for _, frames in symbols:
        for f in frames:
            if not any(f[2] is im for im in images):
                images.append(f[2])
    size, pos = _pack(images)
    atlas = Image.new('RGBA', (size, size))
    for i, im in enumerate(images):
        atlas.paste(im, pos[i])
    def s(text):
        b = text.encode()
        return struct.pack('<I', len(b)) + b
    out = bytearray(b'BILD')
    out += struct.pack('<III', 6, len(symbols), sum(len(f) for _, f in symbols))
    out += s(build_name) + struct.pack('<I', 1) + s('atlas-0.tex')
    verts = []
    for name, frames in symbols:
        out += struct.pack('<II', klei_hash(name), len(frames))
        for num, dur, im, (px, py) in frames:
            idx = next(i for i, other in enumerate(images) if other is im)
            ax, ay = pos[idx]
            w, h = im.size
            l, r, t, b = -px, w - px, -py, h - py
            u0, u1 = ax / size, (ax + w) / size
            vt, vb = 1 - ay / size, 1 - (ay + h) / size
            quad = [(l, t, 0, u0, vt, 0), (r, t, 0, u1, vt, 0), (l, b, 0, u0, vb, 0),
                    (r, t, 0, u1, vt, 0), (r, b, 0, u1, vb, 0), (l, b, 0, u0, vb, 0)]
            out += struct.pack('<II', num, dur) + struct.pack('<ffff', (l + r) / 2, (t + b) / 2, w, h)
            out += struct.pack('<II', len(verts), 6)
            verts += quad
    out += struct.pack('<I', len(verts))
    for v in verts:
        out += struct.pack('<ffffff', *v)
    names = [n for n, _ in symbols]
    out += struct.pack('<I', len(names))
    for n in names:
        out += struct.pack('<I', klei_hash(n)) + s(n)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        def put(name, data):
            zi = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, data)
        put('build.bin', bytes(out))
        put('atlas-0.tex', ktex_dxt5(atlas))
        if anim_bin is not None:
            put('anim.bin', anim_bin)
    return atlas
