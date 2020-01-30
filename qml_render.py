import re
from font import Font
from static import DEFAULT_PROPS, DEFAULT_ZORDERS
from typing import Dict, List
from es_items import Element


class QmlItem:
    def __init__(self, typename: str, props=None):
        self.typename = typename
        self.props: Dict[str, str] = props if props else {}
        self.extra_lines: List[str] = []
        self.childs: List[QmlItem] = []
        self.named_childs: Dict[str, QmlItem] = {}

    def render(self, indent=0):
        lines = [f"{'  ' * indent}{self.typename} {{"]

        subindent = '  ' * (indent + 1)

        prop_lines = [f"{subindent}{key}: {val}" for key, val in self.props.items()]
        prop_lines.sort()
        lines.extend(prop_lines)

        extra_lines = [f"{subindent}{line}" for line in self.extra_lines]
        lines.extend(extra_lines)

        for name, qitem in self.named_childs.items():
            sublines = qitem.render(indent + 1)
            sublines[0] = f"{subindent}{name}: {qitem.typename} {{"
            lines.extend(sublines)

        for qitem in self.childs:
            lines.extend(qitem.render(indent + 1))

        lines.append(f"{'  ' * indent}}}")
        return lines


def print_debug(elem):
    print(f"    - {elem.type} {elem.name} extra:{elem.is_extra}")
    for prop in elem.params:
        print(f"      - {prop}: {elem.params[prop]}")


def font_path_to_name(path: str) -> str:
    clean_path = path.rsplit('/', 1)[1]
    clean_path = re.sub('[^a-zA-Z0-9_]', '_', clean_path)
    clean_path = re.sub('_ttf$', '', clean_path)
    return 'theme_' + clean_path


def prepare_text(text: str) -> str:
    prop_str = text \
        .replace("'", "\\'") \
        .replace('${system.name}', "' + modelData.shortName + '") \
        .replace('${system.theme}', "' + modelData.shortName + '") \
        .replace('${system.fullName}', "' + modelData.name + '")
    return f"'{prop_str}'"


def get_defaults(viewname: str, elemtype: str, elemname: str) -> Dict[str, str]:
    keys = [
        ('*', elemtype, '*'),
        (viewname, elemtype, '*'),
        ('*', elemtype, elemname),
        (viewname, elemtype, elemname),
    ]
    retval: Dict[str, str] = {}
    for key in keys:
        retval = {**retval, **DEFAULT_PROPS.get(key, {})}

    return retval


def es_zorder(elem: Element) -> int:
    if 'zIndex' in elem.params:
        return int(elem.params['zIndex'])

    return DEFAULT_ZORDERS.get(elem.name, 10)


def render_prop_id(elem: Element, props: Dict[str, str]):
    clean_str = re.sub('[^a-zA-Z0-9_]+', '_', elem.name)
    props['id'] = clean_str[0].lower() + clean_str[1:]

    if elem.is_extra:
        props['id'] = 'x_' + props['id']  # to avoid illegal JS names


def render_prop_pos(elem: Element, props: Dict[str, str]):
    if 'pos' in elem.params:
        pair = elem.params['pos']

        if pair.a == 0.0:
            props['x'] = "0"
        else:
            props['x'] = f"{pair.a} * root.width"

        if pair.b == 0.0:
            props['y'] = "0"
        else:
            props['y'] = f"{pair.b} * root.height"

        if 'origin' in elem.params:
            origin = elem.params['origin']
            if origin.a != 0.0:
                props['x'] = f"{props['x']} - {origin.a} * width"
            if origin.b != 0.0:
                props['y'] = f"{props['y']} - {origin.b} * height"


def render_prop_rotation(elem: Element, props: Dict[str, str]):
    if 'rotation' in elem.params:
        angle = elem.params['rotation']
        if angle == 0.0:
            return

        origin = [0.5, 0.5]
        if 'rotationOrigin' in elem.params:
            pair = elem.params['rotationOrigin']
            origin = [pair.a, pair.b]

        props['transform'] = f"Rotation {{ \
            angle: {angle}; \
            origin.x: {origin[0]} * width; \
            origin.y: {origin[1]} * height; \
            }}"


def render_prop_zindex(elem: Element, props: Dict[str, str]):
    if 'zIndex' in elem.params:
        props['z'] = elem.params['zIndex']


def render_prop_visible(elem: Element, props: Dict[str, str]):
    if 'visible' in elem.params:
        if not elem.params['visible']:
            props['visible'] = "false"


def render_prop_opacity(elem: Element, props: Dict[str, str]):
    if 'color' in elem.params:
        color = elem.params['color']
        if len(color.hex) == 8:
            alpha = int(color.hex[-2:], 16)
            props['opacity'] = str(alpha / 255.0)


def create_color_overlay(elem, elem_id: str) -> List[QmlItem]:
    colorfill_id = 'color_' + elem_id

    colorfill = QmlItem('Rectangle')
    colorfill.props = {
        'id': colorfill_id,
        'anchors.fill': elem_id,
        'color': f"'#{elem.params['color'].color}'",
        'visible': 'false',
    }

    blend = QmlItem('Blend')
    blend.props = {
        'anchors.fill': elem_id,
        'source': elem_id,
        'foregroundSource': colorfill_id,
        'mode': "'multiply'",
    }
    opacity = elem.params['color'].opacity
    if opacity < 1.0:
        blend.props['opacity'] = opacity

    return [colorfill, blend]


def render_rgba_color(color) -> str:
    return f"'#{color.hex[6:]}{color.hex[0:6]}'"


def render_prop_fontinfo(elem: Element, props: Dict[str, str]):
    if 'fontPath' in elem.params:
        value = elem.params['fontPath']
        font_id = font_path_to_name(value)
        props['font.family'] = f"{font_id}.name"

        # Try to guess the weight
        if font_id.endswith('light'):
            props['font.weight'] = "Font.Light"
        if font_id.endswith('bold'):
            props['font.weight'] = "Font.Bold"

    if 'fontSize' in elem.params:
        size = elem.params['fontSize']
        props['font.pixelSize'] = f"{size} * root.height"


def render_prop_textinfo(elem: Element, props: Dict[str, str]):
    if 'alignment' in elem.params:
        if elem.params['alignment'] == 'center':
            props['horizontalAlignment'] = "Text.AlignHCenter"
            props['verticalAlignment'] = "Text.AlignVCenter"
        elif elem.params['alignment'] == 'right':
            props['horizontalAlignment'] = "Text.AlignRight"

    if 'forceUppercase' in elem.params:
        if elem.params['forceUppercase']:
            props['font.capitalization'] = "Font.AllUppercase"

    if 'lineSpacing' in elem.params:
        props['lineHeight'] = elem.params['lineSpacing']


def create_image(viewname: str, elem: Element) -> List[QmlItem]:
    qitem = QmlItem('Image')
    qitem.props = get_defaults(viewname, elem.type, elem.name)

    render_prop_id(elem, qitem.props)
    render_prop_pos(elem, qitem.props)
    render_prop_rotation(elem, qitem.props)
    render_prop_opacity(elem, qitem.props)
    render_prop_zindex(elem, qitem.props)
    render_prop_visible(elem, qitem.props)

    if 'path' in elem.params:
        qitem.props['source'] = prepare_text('../' + elem.params['path'])
        if 'default' in elem.params:
            default = prepare_text('../' + elem.params['default'])
            qitem.props['source'] = f"{qitem.props['source']} || {default}"

    if 'source' not in qitem.props:
        # return []
        pass

    if 'size' in elem.params:
        pair = elem.params['size']
        has_width = pair.a != 0.0
        has_height = pair.b != 0.0

        if has_width and has_height:
            qitem.props['fillMode'] = 'Image.Stretch'
            qitem.props['width'] = f"{pair.a} * root.width"
            qitem.props['height'] = f"{pair.b} * root.height"

        if has_width and not has_height:
            qitem.props['width'] = f"{pair.a} * root.width"
            qitem.props['height'] = "width * (implicitHeight || 1) / (implicitWidth || 1)"

        if not has_width and has_height:
            qitem.props['width'] = "height * (implicitWidth || 1) / (implicitHeight || 1)"
            qitem.props['height'] = f"{pair.b} * root.height"

    elif 'maxSize' in elem.params:
        pair = elem.params['maxSize']
        qitem.props['width'] = f"{pair.a} * root.width"
        qitem.props['height'] = f"{pair.b} * root.height"
        qitem.props['fillMode'] = 'Image.PreserveAspectFit'

    if 'tile' in elem.params and elem.params['tile']:
        qitem.props['fillMode'] = 'Image.Tile'

    siblings = []

    if 'color' in elem.params:
        qitem.props['visible'] = 'false'
        qitem.props.pop('opacity', None)
        siblings.extend(create_color_overlay(elem, qitem.props['id']))
        if 'z' in qitem.props:
            siblings[-1].props['z'] = qitem.props.pop('z')

    if 'opacity' not in qitem.props and 'visible' not in qitem.props:
        qitem.extra_lines.append('Behavior on opacity { NumberAnimation { duration: 120 } }')

    return [qitem] + siblings


def create_text(viewname: str, elem: Element, fontmap: Dict[str, Font]) -> List[QmlItem]:
    qitem = QmlItem('Text')
    qitem.props = get_defaults(viewname, elem.type, elem.name)

    render_prop_id(elem, qitem.props)
    render_prop_pos(elem, qitem.props)
    render_prop_rotation(elem, qitem.props)
    render_prop_zindex(elem, qitem.props)
    render_prop_visible(elem, qitem.props)
    render_prop_opacity(elem, qitem.props)
    render_prop_fontinfo(elem, qitem.props)
    render_prop_textinfo(elem, qitem.props)

    if 'fontPath' in elem.params:
        font_name = font_path_to_name(elem.params['fontPath'])
        metrics = fontmap[font_name].metrics

        if 'y' in qitem.props:
            qt, es = metrics.qt_s_y, metrics.es_s_y
            qitem.props['y'] = f"{qitem.props['y']} - font.pixelSize * {(qt - es) / qt}"
        if 'font.pixelSize' in qitem.props:
            qt, es = metrics.qt_baseline, metrics.es_baseline
            qitem.props['font.pixelSize'] = f"{qitem.props['font.pixelSize']} * {es / qt}"
        if 'lineHeight' in qitem.props:
            qt, es = metrics.qt_line_height, metrics.es_line_height
            qitem.props['lineHeight'] = f"{float(qitem.props['lineHeight']) * es / qt}"

    if 'size' in elem.params:
        pair = elem.params['size']
        if pair.a != 0.0:
            qitem.props['width'] = f"{pair.a} * root.width"
            qitem.props['wrapMode'] = "Text.WordWrap"
        if pair.b != 0.0:
            qitem.props['height'] = f"{pair.b} * root.height"
            qitem.props['elide'] = "Text.ElideRight"

    if 'color' in elem.params:
        qitem.props['color'] = render_rgba_color(elem.params['color'])

    if 'backgroundColor' in elem.params:
        bg_item = QmlItem('Rectangle')
        bg_item.props = {
            'anchors.fill': 'parent',
            'color': render_rgba_color(elem.params['backgroundColor']),
            'z': '-1',
        }
        qitem.childs.append(bg_item)

    if elem.type == 'text':
        if 'text' in elem.params:
            qitem.props['text'] = prepare_text(elem.params['text'])

    if elem.type == 'datetime':
        if elem.params.get('displayRelative', False):
            qitem.props['text'] = 'Helpers.relative_date(value)'

        if 'format' in elem.params:
            format_str = elem.params['format'] \
                .replace('%Y', 'yyyy') \
                .replace('%m', 'MM') \
                .replace('%d', 'dd') \
                .replace('%H', 'hh') \
                .replace('%M', 'mm') \
                .replace('%S', 'ss') \
                .replace("'", "\\'")
            qitem.props['readonly property string dateFormat'] = prepare_text(format_str)

    if 'text' not in qitem.props:
        # return []
        pass

    return [qitem]


def create_rating(viewname: str, elem: Element) -> List[QmlItem]:
    qitem = QmlItem('RatingBar')
    qitem.props = get_defaults(viewname, elem.type, elem.name)

    render_prop_id(elem, qitem.props)
    render_prop_pos(elem, qitem.props)
    render_prop_rotation(elem, qitem.props)
    render_prop_zindex(elem, qitem.props)
    render_prop_visible(elem, qitem.props)
    render_prop_opacity(elem, qitem.props)

    if 'filledPath' in elem.params:
        qitem.props['filledPath'] = f"'../{elem.params['filledPath']}'"
    if 'unfilledPath' in elem.params:
        qitem.props['unfilledPath'] = f"'../{elem.params['unfilledPath']}'"

    if 'size' in elem.params:
        pair = elem.params['size']
        if pair.b == 0.0:
            qitem.props['width'] = f"{pair.a} * root.width * 5"
            qitem.props['height'] = 'width / 5'
        elif pair.a == 0.0:
            qitem.props['width'] = 'height * 5'
            qitem.props['height'] = f"{pair.b} * root.height"
#        if pair.a != 0.0:
#            qitem.props['width'] = f"{pair.a} * root.width * 5"
#            qitem.props['height'] = 'width / 5'
#        elif pair.b != 0.0:
#            qitem.props['width'] = 'height * 5'
#            qitem.props['height'] = f"{pair.b} * root.height"

    siblings = []

    if 'color' in elem.params:
        qitem.props['visible'] = 'false'
        qitem.props.pop('opacity', None)
        siblings.extend(create_color_overlay(elem, qitem.props['id']))
        if 'z' in qitem.props:
            siblings[-1].props['z'] = qitem.props.pop('z')

    return [qitem] + siblings


def create_helpsystem(viewname: str, elem: Element) -> List[QmlItem]:
    return []  # Not supported yet

    props = get_defaults(viewname, elem.type, elem.name)

    render_prop_id(elem, props)
    render_prop_pos(elem, props)
    render_prop_fontinfo(elem, props)

    for kind in ['textColor', 'iconColor']:
        props[kind] = "'#777777'"
        if kind in elem.params:
            props[kind] = render_rgba_color(elem.params[kind])

    return []
    return [
        "Utils.HelpSystem {",
        "}",
    ]


def create_textlist(viewname: str, elem: Element, fontmap: Dict[str, Font]) -> List[QmlItem]:
    qlist = QmlItem('ListView')
    qlist.props = get_defaults(viewname, elem.type, elem.name)
    qdelegate = QmlItem('Text')
    qdelegate.props = get_defaults(viewname, elem.type + '__delegate', elem.name + '__delegate')
    qhighlight = QmlItem('Rectangle')

    render_prop_id(elem, qlist.props)
    render_prop_pos(elem, qlist.props)
    render_prop_fontinfo(elem, qdelegate.props)
    render_prop_textinfo(elem, qdelegate.props)
    render_prop_zindex(elem, qlist.props)
    render_prop_visible(elem, qlist.props)

    if 'fontPath' in elem.params:
        font_name = font_path_to_name(elem.params['fontPath'])
        metrics = fontmap[font_name].metrics

        if 'font.pixelSize' in qdelegate.props:
            qt, es = metrics.qt_baseline, metrics.es_baseline
            qdelegate.props['font.pixelSize'] = f"{qdelegate.props['font.pixelSize']} * {es} / {qt}"
        if 'lineHeight' in qdelegate.props:
            qt, es = metrics.qt_line_height, metrics.es_line_height
            qdelegate.props['lineHeight'] = f"{float(qdelegate.props['lineHeight'])} * {es} / {qt}"

    if 'size' in elem.params:
        pair = elem.params['size']
        qlist.props['width'] = f"{pair.a} * root.width"
        qlist.props['height'] = f"{pair.b} * root.height"
        qlist.props['clip'] = "true"

    if 'selectorImagePath' in elem.params:
        qhighlight.typename = 'Image'
        qhighlight.props = {
            'source': "'../" + elem.params['selectorImagePath'] + "'",
            'asynchronous': 'true',
            # 'fillMode': 'Image.Pad',
            'smooth': 'false',
        }
        if 'selectorImageTile' in elem.params:
            if elem.params['selectorImageTile']:
                qhighlight.props['fillMode'] = "Image.PreserveAspectFit"
    else:
        qhighlight.typename = 'Rectangle'
        qhighlight.props = {
            'color': "'#000'"
        }
        if 'selectorColor' in elem.params:
            qhighlight.props['color'] = render_rgba_color(elem.params['selectorColor'])

    if 'fontSize' in elem.params:
        size = elem.params['fontSize']
        qlist.props['readonly property int highlightHeight'] = f"{size} * 1.5 * root.height"

    if 'primaryColor' in elem.params:
        qdelegate.props['readonly property color unselectedColor'] = render_rgba_color(elem.params['primaryColor'])
        qdelegate.props['color'] = 'unselectedColor'
    if 'selectedColor' in elem.params:
        qdelegate.props['readonly property color selectedColor'] = render_rgba_color(elem.params['selectedColor'])
    if 'primaryColor' in elem.params and 'selectedColor' in elem.params:
        qdelegate.props['color'] = 'ListView.isCurrentItem ? selectedColor : unselectedColor'

    if 'horizontalMargin' in elem.params:
        pad = elem.params['horizontalMargin']
        qdelegate.props['leftPadding'] = f'{pad} * root.width'
        qdelegate.props['rightPadding'] = 'leftPadding'

    qlist.named_childs = {
        'delegate': qdelegate,
        'highlight': qhighlight,
    }
    return [qlist]


def create_scrolltext(viewname: str, elem: Element, fontmap: Dict[str, Font]) -> List[QmlItem]:
    qtext = create_text(viewname, elem, fontmap)[0]

    container_id = qtext.props.pop('id')
    inner_id = container_id + '_inner'
    scroll_id = container_id + '_scroll'

    qcontainer = QmlItem('Flickable')
    qcontainer.props = get_defaults(viewname, elem.type + '__flick', elem.name + '__flick')
    for key in qcontainer.props:
        qcontainer.props[key] = qcontainer.props[key].replace('$INNERID', inner_id)
        qcontainer.props[key] = qcontainer.props[key].replace('$SCROLLID', scroll_id)

    for key in ['x', 'y', 'width', 'height']:
        if key in qtext.props:
            qcontainer.props[key] = qtext.props \
                .pop(key) \
                .replace(' font.', f" {inner_id}.font.")

    qtext.props['width'] = 'parent.width'
    qtext.props['id'] = inner_id
    qcontainer.props['id'] = container_id

    qanim = QmlItem('SequentialAnimation on contentY')
    qanim.props = {
        'id': scroll_id,
        'loops': 'Animation.Infinite',
    }
    qanim.childs.append(QmlItem('PauseAnimation', {'duration': '1000'}))
    qanim.childs.append(QmlItem('PropertyAnimation', {
        'to': f"Math.max(0, {container_id}.contentHeight - {container_id}.height)",
        'duration': f"{inner_id}.lineCount * 1000",
    }))
    qanim.childs.append(QmlItem('PauseAnimation', {'duration': '3000'}))
    qanim.childs.append(QmlItem('PropertyAnimation', {'to': '0', 'duration': '500'}))

    qcontainer.childs.append(qanim)
    qcontainer.childs.append(qtext)
    return [qcontainer]


def render_view_items(viewname: str, elems: List[Element], fontmap: Dict[str, Font]) -> List[str]:
    elems = sorted(elems, key=es_zorder)
    # print(f"  - {viewname}: {len(elems)} elem")

    qroot = QmlItem('FocusScope')
    qroot.props = {
        'id': 'root',
        'enabled': 'focus',
        'focus': 'parent.focus',
        'clip': 'true',
    }

    if viewname != 'system':
        if viewname == 'grid':
            holder = 'gamegrid'
        else:
            holder = 'gamelist'
        qroot.props['readonly property alias currentGame'] = f"{holder}.currentGame"

    for elem in elems:
        # print(platform_name, viewname, elem.type, elem.name)

        if elem.type == 'image':
            if not (viewname == 'system' and elem.name == 'logo'):
                qroot.childs.extend(create_image(viewname, elem))
            continue
        if elem.type == 'text':
            if elem.name == 'md_description' and not elem.is_extra:
                qroot.childs.extend(create_scrolltext(viewname, elem, fontmap))
                continue
            if viewname == 'system' and elem.name in ['systemInfo', 'logoText']:
                # Handled separately
                continue
            qroot.childs.extend(create_text(viewname, elem, fontmap))
            continue
        if elem.type == 'datetime':
            qroot.childs.extend(create_text(viewname, elem, fontmap))
            continue
        if elem.type == 'rating':
            qroot.childs.extend(create_rating(viewname, elem))
            continue
        if elem.type == 'helpsystem':
            qroot.childs.extend(create_helpsystem(viewname, elem))
            continue
        if elem.type == 'textlist':
            qroot.childs.extend(create_textlist(viewname, elem, fontmap))
            continue
        if elem.type == 'carousel':
            # Handled separately
            continue
        print_debug(elem)

    return [
        "import QtQuick 2.6",
        "import QtGraphicalEffects 1.0",
        "import '../__components'",
        "import '../__components/helpers.js' as Helpers",
    ] + qroot.render()
