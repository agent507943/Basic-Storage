import os, json
from xml.etree import ElementTree as ET

BASE = os.path.dirname(__file__)
COMPONENTS_FILE = os.path.join(BASE, 'components.json')
IMAGES_DIR = os.path.join(BASE, 'static', 'images')
REAL_DIR = os.path.join(IMAGES_DIR, 'real')


def parse_translate(t):
    if not t: return (0.0, 0.0)
    t = t.strip()
    if t.startswith('translate'):
        inside = t[t.find('(')+1:t.find(')')]
        parts = [p for p in inside.replace(',', ' ').split() if p]
        try:
            if len(parts) == 1:
                return (float(parts[0]), 0.0)
            return (float(parts[0]), float(parts[1]))
        except Exception:
            return (0.0, 0.0)
    return (0.0, 0.0)


def parse_svg_connectors(svg_path):
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except Exception as e:
        print('Failed parse', svg_path, e)
        return {}

    connectors = {}

    def walk(el, acc_tx=0.0, acc_ty=0.0):
        tr = el.get('transform')
        tx, ty = parse_translate(tr)
        cur_tx = acc_tx + tx
        cur_ty = acc_ty + ty
        data_conn = el.get('data-conn') or el.get('data-conn')
        if data_conn:
            cx = el.get('cx')
            cy = el.get('cy')
            if cx is not None and cy is not None:
                try:
                    x = float(cx) + cur_tx
                    y = float(cy) + cur_ty
                    connectors[data_conn] = {'x': x, 'y': y}
                except Exception:
                    pass
            else:
                xattr = el.get('x'); yattr = el.get('y')
                wattr = el.get('width'); hattr = el.get('height')
                try:
                    if xattr and yattr and wattr and hattr:
                        x = float(xattr) + float(wattr)/2 + cur_tx
                        y = float(yattr) + float(hattr)/2 + cur_ty
                        connectors[data_conn] = {'x': x, 'y': y}
                except Exception:
                    pass
        for child in list(el):
            walk(child, cur_tx, cur_ty)

    walk(root, 0.0, 0.0)
    return connectors


def svg_viewbox(svg_path):
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        vb = root.get('viewBox')
        if vb:
            parts = [float(p) for p in vb.strip().split()]
            return (parts[2], parts[3])
        w = root.get('width'); h = root.get('height')
        if w and h:
            try:
                return (float(w), float(h))
            except Exception:
                pass
    except Exception:
        pass
    return (None, None)


def main():
    with open(COMPONENTS_FILE, 'r', encoding='utf-8') as f:
        comps = json.load(f)
    changed = 0
    for c in comps:
        img = c.get('image')
        if not img or not img.lower().endswith('.svg'):
            continue
        svg_path = os.path.join(IMAGES_DIR, img)
        if not os.path.exists(svg_path):
            svg_path = os.path.join(REAL_DIR, img)
            if not os.path.exists(svg_path):
                print('SVG not found for', c.get('id'), img)
                continue
        svg_w, svg_h = svg_viewbox(svg_path)
        if not svg_w or not svg_h:
            print('No viewbox for', svg_path)
            continue
        conn_map = parse_svg_connectors(svg_path)
        box = c.get('svg') or {}
        bx = box.get('x', 0); by = box.get('y', 0); bw = box.get('w', box.get('width', 0)); bh = box.get('h', box.get('height', 0))
        if not bw or not bh:
            print('No box size for', c.get('id'))
            continue
        new_conns = []
        for k, v in conn_map.items():
            parts = k.split('.')
            conn_id = parts[-1]
            sx = bx + (v['x'] / svg_w) * bw
            sy = by + (v['y'] / svg_h) * bh
            new_conns.append({'id': conn_id, 'x': round(sx,1), 'y': round(sy,1)})
        if new_conns:
            c['connectors'] = new_conns
            changed += 1
            print('Updated', c.get('id'), 'connectors:', new_conns)
    if changed:
        with open(COMPONENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(comps, f, indent=2)
    print('Refresh complete. Components updated:', changed)

if __name__ == '__main__':
    main()
