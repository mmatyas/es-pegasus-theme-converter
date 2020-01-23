import re
from static import DEFAULT_PROPS, DEFAULT_ZORDERS, RESERVED_ITEMS, RESTRICTED_TYPES
from errors import warn
from typing import Dict, List
from es_items import Element


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


def render_props(props: Dict[str, str], indent=1) -> List[str]:
    lines = [f"{'  ' * indent}{key}: {val}" for key, val in props.items()]
    lines.sort()
    return lines


def render_prop_id(elem: Element, props: Dict[str, str]):
    clean_str = re.sub('[^a-zA-Z0-9_]+', '_', elem.name)
    props['id'] = clean_str[0].lower() + clean_str[1:]

    # FIXME: handle non-extra items marked as extra on the XML side
    # if elem.is_extra:
    #     props['id'] = 'x_' + props['id']  # to avoid illegal JS names


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


def render_prop_color_overlay(elem, elem_id: str) -> List[str]:
    colorfill_id = 'color_' + elem_id
    props = {
        'id': colorfill_id,
        'anchors.fill': elem_id,
        'color': f"'#{elem.params['color'].color}'",
        'visible': 'false',
    }
    lines = [
        "Rectangle {",
        *render_props(props),
        "}",
    ]

    props = {
        'anchors.fill': elem_id,
        'source': elem_id,
        'foregroundSource': colorfill_id,
        'mode': "'multiply'",
    }

    opacity = elem.params['color'].opacity
    if opacity < 1.0:
        props['opacity'] = opacity

    lines.extend([
        "Blend {",
        *render_props(props),
        "}",
    ])

    return lines


def create_rgba_color(color) -> str:
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


def render_image(viewname: str, elem: Element) -> List[str]:
    props = get_defaults(viewname, elem.type, elem.name)
    sibling_lines = []

    render_prop_id(elem, props)
    render_prop_pos(elem, props)
    render_prop_rotation(elem, props)
    render_prop_opacity(elem, props)
    render_prop_zindex(elem, props)
    render_prop_visible(elem, props)

    if 'size' in elem.params:
        pair = elem.params['size']
        has_width = pair.a != 0.0
        has_height = pair.b != 0.0

        if has_width and has_height:
            props['fillMode'] = 'Image.Stretch'
            props['width'] = f"{pair.a} * root.width"
            props['height'] = f"{pair.b} * root.height"

        if has_width and not has_height:
            props['width'] = f"{pair.a} * root.width"

        if not has_width and has_height:
            props['height'] = f"{pair.b} * root.height"

    elif 'maxSize' in elem.params:
        pair = elem.params['maxSize']
        props['width'] = f"{pair.a} * root.width"
        props['height'] = f"{pair.b} * root.height"
        props['fillMode'] = 'Image.PreserveAspectFit'

    if 'tile' in elem.params and elem.params['tile']:
        props['fillMode'] = 'Image.Tile'

    if 'path' in elem.params:
        props['source'] = prepare_text('../' + elem.params['path'])
        if 'default' in elem.params:
            default = prepare_text('../' + elem.params['default'])
            props['source'] = f"{props['source']} || {default}"

    if 'source' not in props:
        # return []
        pass

    if 'color' in elem.params:
        props['visible'] = 'false'
        props.pop('opacity', None)
        sibling_lines = render_prop_color_overlay(elem, props['id'])

    lines = [
        "Image {",
        *render_props(props),
        "}",
        *sibling_lines,
    ]
    if 'opacity' not in props and 'visible' not in props:
        lines.insert(len(lines) - 1, '  Behavior on opacity { NumberAnimation { duration: 120 } }')

    return lines


def render_text(viewname: str, elem: Element) -> List[str]:
    props = get_defaults(viewname, elem.type, elem.name)
    childs = []

    render_prop_id(elem, props)
    render_prop_pos(elem, props)
    render_prop_rotation(elem, props)
    render_prop_zindex(elem, props)
    render_prop_visible(elem, props)
    render_prop_opacity(elem, props)
    render_prop_fontinfo(elem, props)
    render_prop_textinfo(elem, props)

    if 'size' in elem.params:
        pair = elem.params['size']
        if pair.a != 0.0:
            props['width'] = f"{pair.a} * root.width"
            props['wrapMode'] = "Text.WordWrap"
        if pair.b != 0.0:
            props['height'] = f"{pair.b} * root.height"
            props['elide'] = "Text.ElideRight"

    if 'color' in elem.params:
        props['color'] = create_rgba_color(elem.params['color'])

    if 'backgroundColor' in elem.params:
        color_str = create_rgba_color(elem.params['backgroundColor'])
        childs.append(f"Rectangle {{ anchors.fill: parent; color: '{color_str}'; z: -1 }}")

    if elem.type == 'text':
        if 'text' in elem.params:
            props['text'] = prepare_text(elem.params['text'])

    if elem.type == 'datetime':
        if elem.params.get('displayRelative', False):
            props['text'] = 'Helpers.relative_date(value)'

        if 'format' in elem.params:
            format_str = elem.params['format'] \
                .replace('%Y', 'yyyy') \
                .replace('%m', 'MM') \
                .replace('%d', 'dd') \
                .replace('%H', 'hh') \
                .replace('%M', 'mm') \
                .replace('%S', 'ss') \
                .replace("'", "\\'")
            props['readonly property string dateFormat'] = prepare_text(format_str)

    if 'text' not in props:
        # return []
        pass

    return [
        "Text {",
        *render_props(props),
        *[f"  {line}" for line in childs],
        "}"
    ]


def render_rating(viewname: str, elem: Element) -> List[str]:
    props = get_defaults(viewname, elem.type, elem.name)
    sibling_lines = []

    render_prop_id(elem, props)
    render_prop_pos(elem, props)
    render_prop_rotation(elem, props)
    render_prop_zindex(elem, props)
    render_prop_visible(elem, props)
    render_prop_opacity(elem, props)

    if 'filledPath' in elem.params:
        props['filledPath'] = f"'../{elem.params['filledPath']}'"
    if 'unfilledPath' in elem.params:
        props['unfilledPath'] = f"'../{elem.params['unfilledPath']}'"

    if 'size' in elem.params:
        pair = elem.params['size']
        if pair.b == 0.0:
            props['width'] = f"{pair.a} * root.width * 5"
            props['height'] = 'width / 5'
        elif pair.a == 0.0:
            props['width'] = 'height * 5'
            props['height'] = f"{pair.b} * root.height"
#        if pair.a != 0.0:
#            props['width'] = f"{pair.a} * root.width * 5"
#            props['height'] = 'width / 5'
#        elif pair.b != 0.0:
#            props['width'] = 'height * 5'
#            props['height'] = f"{pair.b} * root.height"

    if 'color' in elem.params:
        props['visible'] = 'false'
        props.pop('opacity', None)
        sibling_lines = render_prop_color_overlay(elem, props['id'])

    lines = [
        "RatingBar {",
        *render_props(props),
        "}",
        *sibling_lines,
    ]

    return lines


def render_helpsystem(viewname: str, elem: Element) -> List[str]:
    props = get_defaults(viewname, elem.type, elem.name)

    render_prop_id(elem, props)
    render_prop_pos(elem, props)
    render_prop_fontinfo(elem, props)

    for kind in ['textColor', 'iconColor']:
        props[kind] = "'#777777'"
        if kind in elem.params:
            props[kind] = create_rgba_color(elem.params[kind])

    return []
    return [
        "Utils.HelpSystem {",
        *render_props(props),
        "}",
    ]


def render_textlist(viewname: str, elem: Element) -> List[str]:
    list_props = get_defaults(viewname, elem.type, elem.name)
    delegate_props = get_defaults(viewname, elem.type + '__delegate', elem.name + '__delegate')

    render_prop_id(elem, list_props)
    render_prop_pos(elem, list_props)
    render_prop_fontinfo(elem, delegate_props)
    render_prop_textinfo(elem, delegate_props)
    render_prop_zindex(elem, list_props)
    render_prop_visible(elem, list_props)

    if 'size' in elem.params:
        pair = elem.params['size']
        list_props['width'] = f"{pair.a} * root.width"
        list_props['height'] = f"{pair.b} * root.height"
        list_props['clip'] = "true"

    if 'selectorImagePath' in elem.params:
        hl_type = 'Image'
        hl_props = {
            'source': "'../" + elem.params['selectorImagePath'] + "'",
            'asynchronous': 'true',
            # 'fillMode': 'Image.Pad',
            'smooth': 'false',
        }
        if 'selectorImageTile' in elem.params:
            if elem.params['selectorImageTile']:
                hl_props['fillMode'] = "Image.PreserveAspectFit"
    else:
        hl_type = 'Rectangle'
        hl_props = {
            'color': "'#000'"
        }
        if 'selectorColor' in elem.params:
            hl_props['color'] = create_rgba_color(elem.params['selectorColor'])

    if 'fontSize' in elem.params:
        size = elem.params['fontSize']
        list_props['readonly property int highlightHeight'] = f"{size} * 1.5 * root.height"

    list_props['highlight'] = f"{hl_type} {{ {'; '.join(render_props(hl_props, indent=0))}; }}"

    if 'primaryColor' in elem.params:
        delegate_props['readonly property color unselectedColor'] = create_rgba_color(elem.params['primaryColor'])
        delegate_props['color'] = 'unselectedColor'
    if 'selectedColor' in elem.params:
        delegate_props['readonly property color selectedColor'] = create_rgba_color(elem.params['selectedColor'])
    if 'primaryColor' in elem.params and 'selectedColor' in elem.params:
        delegate_props['color'] = 'ListView.isCurrentItem ? selectedColor : unselectedColor'

    if 'horizontalMargin' in elem.params:
        pad = elem.params['horizontalMargin']
        delegate_props['leftPadding'] = f'{pad} * root.width'
        delegate_props['rightPadding'] = 'leftPadding'

    return [
        "ListView {",
        *render_props(list_props),
        "  delegate: Text {",
        *render_props(delegate_props, indent=2),
        "  }",
        "}",
    ]


def render_view_items(viewname: str, platform_name: str, elems: List[Element]) -> List[str]:
    elems = sorted(elems, key=lambda elem: elem.name)
    elems = sorted(elems, key=es_zorder)
    # print(f"  - {viewname}: {len(elems)} elem")
    lines = [
        "id: root",
        "enabled: focus",
        "focus: parent.focus",
        "clip: true",
    ]

    if viewname != 'system':
        if viewname == 'grid':
            holder = 'gamegrid'
        else:
            holder = 'gamelist'
        lines.append(f"readonly property alias currentGame: {holder}.currentGame")

    reserved_items: Dict[str, str] = RESERVED_ITEMS.get(viewname, {})

    for elem in elems:
        if elem.is_extra:
            if elem.type in RESTRICTED_TYPES:
                warn(f"{platform_name}, {viewname} view: `{elem.name}` cannot be created as an extra element, "
                     "because it doesn't have anything to display on its own")
                continue
            if elem.name in reserved_items:
                warn(f"{platform_name}, {viewname} view: `{elem.name}` is marked as extra, "
                     f"but there's a non-extra item with the same name. This isn't well supported "
                     "at the moment, expect issues.")
                # elem.is_extra = False
                # continue

        if not elem.is_extra:
            if elem.name not in reserved_items:
                warn(f"{platform_name}, {viewname} view: `{elem.name}` is not marked as extra, "
                     f"but no items with such name exist in this view. Entry ignored.")
                continue

            expected_type = reserved_items[elem.name]
            if elem.type != expected_type:
                warn(f"{platform_name}, {viewname} view: `{elem.type}` properties are set for `{elem.name}`, "
                     f"but the type of that is `{expected_type}`. Properties ignored.")
                continue

        # print(platform_name, viewname, elem.type, elem.name)

        if elem.type == 'image':
            if not (viewname == 'system' and elem.name == 'logo'):
                lines.extend(render_image(viewname, elem))
            continue
        if elem.type == 'text':
            if not (viewname == 'system' and elem.name in ['systemInfo', 'logoText']):
                lines.extend(render_text(viewname, elem))
            continue
        if elem.type == 'datetime':
            lines.extend(render_text(viewname, elem))
            continue
        if elem.type == 'rating':
            lines.extend(render_rating(viewname, elem))
            continue
        if elem.type == 'helpsystem':
            lines.extend(render_helpsystem(viewname, elem))
            continue
        if elem.type == 'textlist':
            lines.extend(render_textlist(viewname, elem))
            continue
        print_debug(elem)

    return [
        "import QtQuick 2.6",
        "import QtGraphicalEffects 1.0",
        "import '../__components'",
        "import '../__components/helpers.js' as Helpers",
        "FocusScope {",
        *[f"  {line}" for line in lines],
        "}",
    ]
