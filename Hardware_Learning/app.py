from flask import Flask, render_template, jsonify, request
import os
import json
from xml.etree import ElementTree as ET
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(__file__)
COMPONENTS_FILE = os.path.join(BASE_DIR, 'components.json')
QUESTIONS_FILE = os.path.join(BASE_DIR, 'questions.json')
STUDY_FILE = os.path.join(BASE_DIR, 'study_content.md')
REVIEW_FILE = os.path.join(BASE_DIR, 'review_list.json')
WIRING_ATTEMPTS_FILE = os.path.join(BASE_DIR, 'wiring_attempts.json')
IMAGES_DIR = os.path.join(BASE_DIR, 'static', 'images')
REAL_IMAGES_DIR = os.path.join(IMAGES_DIR, 'real')

os.makedirs(REAL_IMAGES_DIR, exist_ok=True)

app = Flask(__name__, static_folder='static', template_folder='templates')


def load_components():
    try:
        with open(COMPONENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def load_study():
    try:
        with open(STUDY_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ''


def load_review():
    try:
        if os.path.exists(REVIEW_FILE):
            with open(REVIEW_FILE, 'r', encoding='utf-8') as rf:
                return json.load(rf)
    except Exception:
        pass
    return []


def load_questions():
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def parse_svg_and_get_connectors(svg_path):
    """Parse an SVG file and return a dict of connectors with absolute positions in the SVG coordinate space.
    Supports nested translate(x,y) group transforms.
    Returns: { 'data-conn-id': { 'x':float, 'y':float } }
    """
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except Exception:
        return {}

    ns = {'svg': 'http://www.w3.org/2000/svg'}

    def parse_translate(t):
        # very small parser for translate(tx,ty) or translate(tx)
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

    connectors = {}

    def walk(el, acc_tx=0.0, acc_ty=0.0):
        # accumulate translate transforms only
        tr = el.get('transform')
        tx, ty = parse_translate(tr)
        cur_tx = acc_tx + tx
        cur_ty = acc_ty + ty

        # check if element itself is a connector (has data-conn attribute)
        data_conn = el.get('data-conn') or el.get('{http://www.w3.org/1999/xlink}data-conn')
        if data_conn is None:
            # also allow attribute without namespace
            data_conn = el.get('data-conn')

        if data_conn:
            # try common position attributes: cx/cy, x/y
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
                # rect center fallback
                xattr = el.get('x'); yattr = el.get('y')
                wattr = el.get('width'); hattr = el.get('height')
                try:
                    if xattr and yattr and wattr and hattr:
                        x = float(xattr) + float(wattr)/2 + cur_tx
                        y = float(yattr) + float(hattr)/2 + cur_ty
                        connectors[data_conn] = {'x': x, 'y': y}
                except Exception:
                    pass

        # recurse
        for child in list(el):
            walk(child, cur_tx, cur_ty)

    walk(root, 0.0, 0.0)
    return connectors


def svg_viewbox_size(svg_path):
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


def save_review(lst):
    try:
        with open(REVIEW_FILE, 'w', encoding='utf-8') as rf:
            json.dump(lst, rf, indent=2)
    except Exception:
        pass


def load_wiring_attempts():
    try:
        if os.path.exists(WIRING_ATTEMPTS_FILE):
            with open(WIRING_ATTEMPTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return []


def save_wiring_attempts(lst):
    try:
        with open(WIRING_ATTEMPTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(lst, f, indent=2)
    except Exception:
        pass


@app.route('/')
def index():
    comps = load_components()
    study = load_study()
    review = load_review()
    questions = load_questions()
    return render_template('index.html', components=comps, study=study, review_count=len(review), questions=questions)


@app.route('/api/components')
def api_components():
    return jsonify(load_components())


@app.route('/api/components/refresh', methods=['POST'])
def api_components_refresh():
    """Scan component images (SVG) and update connector coords in components.json by mapping SVG coords into the main diagram coordinate space."""
    comps = load_components()
    changed = 0
    for c in comps:
        img = c.get('image')
        if not img or not img.lower().endswith('.svg'):
            continue
        svg_path = os.path.join(IMAGES_DIR, img)
        if not os.path.exists(svg_path):
            # try in real/ subdir
            svg_path = os.path.join(REAL_IMAGES_DIR, img)
            if not os.path.exists(svg_path):
                continue

        svg_w, svg_h = svg_viewbox_size(svg_path)
        if not svg_w or not svg_h:
            continue

        conn_map = parse_svg_and_get_connectors(svg_path)
        # map into main diagram coords using component svg box
        box = c.get('svg') or {}
        bx = box.get('x', 0); by = box.get('y', 0); bw = box.get('w', box.get('width', 0)); bh = box.get('h', box.get('height', 0))
        new_connectors = []
        for k, v in conn_map.items():
            # data-conn formatted like 'component.connector' or full id
            parts = k.split('.')
            conn_id = parts[-1]
            # scale
            sx = bx + (v['x'] / svg_w) * bw
            sy = by + (v['y'] / svg_h) * bh
            new_connectors.append({'id': conn_id, 'x': round(sx,1), 'y': round(sy,1)})

        if new_connectors:
            c['connectors'] = new_connectors
            changed += 1

    # save back
    if changed:
        try:
            with open(COMPONENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(comps, f, indent=2)
        except Exception:
            pass
    return jsonify({'ok': True, 'updated_components': changed})


@app.route('/api/components/save', methods=['POST'])
def api_components_save():
    data = request.get_json() or {}
    comp_id = data.get('id')
    connectors = data.get('connectors')
    if not comp_id or connectors is None:
        return jsonify({'ok': False, 'error': 'missing id or connectors'}), 400
    comps = load_components()
    found = False
    for c in comps:
        if c.get('id') == comp_id:
            # update connector coords (absolute in main diagram coords expected)
            c['connectors'] = connectors
            found = True
            break
    if not found:
        return jsonify({'ok': False, 'error': 'component not found'}), 404
    try:
        with open(COMPONENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(comps, f, indent=2)
    except Exception:
        return jsonify({'ok': False, 'error': 'save failed'}), 500
    return jsonify({'ok': True})


@app.route('/api/upload_image', methods=['POST'])
def api_upload_image():
    if 'file' not in request.files:
        return jsonify({'ok': False, 'error': 'no file'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'ok': False, 'error': 'empty filename'}), 400
    filename = secure_filename(f.filename)
    save_path = os.path.join(REAL_IMAGES_DIR, filename)
    try:
        f.save(save_path)
        return jsonify({'ok': True, 'path': 'real/' + filename})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/questions')
def api_questions():
    return jsonify(load_questions())


@app.route('/api/review/add', methods=['POST'])
def api_review_add():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'ok': False, 'error': 'missing name'}), 400
    lst = load_review()
    if name not in lst:
        lst.append(name)
        save_review(lst)
    return jsonify({'ok': True, 'count': len(lst)})


@app.route('/api/review/list')
def api_review_list():
    return jsonify(load_review())


@app.route('/api/wiring_attempt', methods=['POST'])
def api_wiring_attempt():
    data = request.get_json() or {}
    qid = data.get('question_id')
    frm = data.get('from')
    to = data.get('to')
    ok = bool(data.get('ok'))
    attempt = {
        'question_id': qid,
        'from': frm,
        'to': to,
        'ok': ok
    }
    lst = load_wiring_attempts()
    lst.append(attempt)
    save_wiring_attempts(lst)
    # if incorrect, add to review list (by question id)
    if not ok and qid:
        review = load_review()
        if qid not in review:
            review.append(qid)
            save_review(review)
    return jsonify({'ok': True, 'saved': True, 'count': len(lst)})


if __name__ == '__main__':
    app.run(debug=True, port=8000)
