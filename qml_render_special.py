from es_items import Element
from qml_render import QmlItem, render_prop_id, render_prop_pos, render_rgba_color, create_text
from typing import Dict


DEFAULT_PROPS: Dict[str, Dict[str, str]] = {
    'container': {
    },
    'pathview': {
        'id': 'logoAxis',
        'focus': 'true',
        'anchors.fill': 'parent',
        'Keys.onPressed':
            'if (!event.isAutoRepeat && api.keys.isAccept(event)) ' +
            '{ event.accepted = true; return root.enter(); }',
        'snapMode': 'PathView.SnapOneItem',
        'preferredHighlightBegin': '0.5',
        'preferredHighlightEnd': '0.5',
        'readonly property int pathLength': 'pathItemCount * itemMainLength',
    },
    'pathview_delegate': {
        'readonly property bool selected': 'PathView.isCurrentItem',
        'opacity': 'selected ? 1.0 : 0.5',
    },
    'pathview_delegate_image': {
        'id': 'logoImage',
        'anchors.fill': 'parent',
        'asynchronous': 'true',
        'smooth': 'false',
        'readonly property string sourceRelPath':
            "{ "
            "let path = g_PLATFORM_LOGOS.get(modelData.shortName); "
            "if (path) return path;"
            "path = g_PLATFORM_LOGOS.get('__generic');"
            "if (path) return path"
            ".replace('${system.name}', modelData.shortName)"
            ".replace('${system.theme}', modelData.shortName);"
            "return null; }",
        'source': "(sourceRelPath && `../${sourceRelPath}`) || ''",
        'fillMode': 'Image.PreserveAspectFit',
        'visible': 'status == Image.Ready',
        'opacity': 'visible ? 1.0 : 0.0',
    },
    'pathview_delegate_text': {
        'textFormat': "Text.PlainText",
        'id': "logoText",
        'anchors.centerIn': "parent",
        'color': "'#000'",
        'text': "shortName || longName",
        'font.pixelSize': "0.085 * Window.height",
        'visible': "logoImage.status != Image.Loading && logoImage.status != Image.Ready",
    },
}


def create_carousel_path(carousel: QmlItem, elem: Element) -> QmlItem:
    carousel_id = carousel.props['id']
    qpath = QmlItem('Path')
    qpathline = QmlItem('PathLine')

    item_count = elem.params['maxLogoCount']
    if elem.params['type'].endswith('wheel'):
        buffered_item_count = 2 * 2
        item_count += buffered_item_count

    if elem.params['type'].startswith('horizontal'):
        qpath.props.update({
            'startX': f"({carousel_id}.width - {carousel_id}.pathLength) / 2",
            'startY': f"{carousel_id}.height / 2",
        })
        qpathline.props = {
            'x': f"{carousel_id}.path.startX + {carousel_id}.pathLength",
            'y': f"{carousel_id}.path.startY",
        }
        carousel.props['readonly property int itemMainLength'] = f"width / {item_count}"

    if elem.params['type'].startswith('vertical'):
        qpath.props.update({
            'startX': f"{carousel_id}.width / 2",
            'startY': f"({carousel_id}.height - {carousel_id}.pathLength) / 2",
        })
        qpathline.props = {
            'x': f"{carousel_id}.path.startX",
            'y': f"{carousel_id}.path.startY + {carousel_id}.pathLength",
        }
        carousel.props['readonly property int itemMainLength'] = f"height / {item_count}"

    if elem.params['type'].endswith('wheel'):
        qattrib = QmlItem('PathAttribute')
        qattrib.props = {
            'name': "'itemRotation'",
            'value': f"{carousel_id}.pathItemCount / -2 * {float(elem.params['logoRotation'])}",
        }
        qpath.childs.append(qattrib)

    qpath.childs.append(qpathline)

    if elem.params['type'].endswith('wheel'):
        qattrib = QmlItem('PathAttribute')
        qattrib.props = {
            'name': "'itemRotation'",
            'value': f"{carousel_id}.pathItemCount / 2 * {float(elem.params['logoRotation'])}",
        }
        qpath.childs.append(qattrib)

    return qpath


def create_carousel_delegate(carousel: QmlItem, elem: Element) -> QmlItem:
    qdelegate = QmlItem('Item')
    qdelegate.props = DEFAULT_PROPS['pathview_delegate']

    if elem.params['type'].startswith('horizontal'):
        qdelegate.props.update({
            'width': 'PathView.view.itemMainLength',
            'height': 'PathView.view.height',
        })
    if elem.params['type'].startswith('vertical'):
        qdelegate.props.update({
            'width': 'PathView.view.width',
            'height': 'PathView.view.itemMainLength',
        })

    qinnerbox = QmlItem('Item')
    qinnerbox.props['id'] = 'innerDelegate'

    alignment = elem.params['logoAlignment']
    if alignment == 'center':
        qinnerbox.props['anchors.centerIn'] = 'parent'
    else:
        qinnerbox.props[f'anchors.{alignment}'] = f'parent.{alignment}'

    if alignment == 'left' or alignment == 'right':
        qinnerbox.props[f'anchors.{alignment}Margin'] = f'width * 0.1'
    if alignment == 'top' or alignment == 'bottom':
        qinnerbox.props[f'anchors.{alignment}Margin'] = f'height * 0.1'

    if elem.params['type'].startswith('horizontal'):
        qinnerbox.props['anchors.horizontalCenter'] = 'parent.horizontalCenter'
    if elem.params['type'].startswith('vertical'):
        qinnerbox.props['anchors.verticalCenter'] = 'parent.verticalCenter'

    # NOTE: manual scale to respect the anchor sides
    size = elem.params['logoSize']
    qinnerbox.props.update({
        'width': f"(selected ? {elem.params['logoScale']} : 1.0) * {size.a} * root.width",
        'height': f"(selected ? {elem.params['logoScale']} : 1.0) * {size.b} * root.height",
    })
    for side in ['width', 'height']:
        qinnerbox.extra_lines.append(f'Behavior on {side} {{ NumberAnimation {{ duration: 200 }} }}')

    if elem.params['type'].endswith('wheel'):
        origin = elem.params['logoRotationOrigin']
        transform = QmlItem('Rotation')
        transform.props = {
            'origin.x': f"{qinnerbox.props['id']}.width * {origin.a}",
            'origin.y': f"{qinnerbox.props['id']}.height * {origin.b}",
            'angle': f"{qinnerbox.props['id']}.parent.PathView.itemRotation",
        }
        qinnerbox.named_childs['transform'] = transform

    default_key = 'pathview_delegate_image'
    qinnerbox.childs.append(QmlItem('Image'))
    qinnerbox.childs[-1].props = DEFAULT_PROPS[default_key]
    qinnerbox.childs[-1].extra_lines = ['Behavior on opacity { NumberAnimation { duration: 120 } }']

    default_key = 'pathview_delegate_text'
    qinnerbox.childs.append(QmlItem('Text'))
    qinnerbox.childs[-1].props = DEFAULT_PROPS[default_key]

    qdelegate.childs.append(qinnerbox)
    return qdelegate


def create_systemcarousel(elem: Element) -> QmlItem:
    # TODO input check

    qcontainer = QmlItem('Rectangle')
    qcontainer.props = DEFAULT_PROPS['container']

    render_prop_id(elem, qcontainer.props)
    render_prop_pos(elem, qcontainer.props)

    size = elem.params['size']
    qcontainer.props.update({
        'width': f"{size.a} * root.width",
        'height': f"{size.b} * root.height",
        'color': render_rgba_color(elem.params['color']),
    })

    qcarousel = QmlItem('PathView')
    qcarousel.props = DEFAULT_PROPS['pathview']

    if elem.params['type'].startswith('horizontal'):
        qcarousel.props.update({
            'Keys.onLeftPressed': 'decrementCurrentIndex()',
            'Keys.onRightPressed': 'incrementCurrentIndex()',
            'pathItemCount':
                '{ let count = Math.ceil(width / itemMainLength); '
                'return (count + 2 <= model.count) ? count + 2 : Math.min(count, model.count); }',
        })
    if elem.params['type'].startswith('vertical'):
        qcarousel.props.update({
            'Keys.onUpPressed': 'decrementCurrentIndex()',
            'Keys.onDownPressed': 'incrementCurrentIndex()',
            'pathItemCount':
                '{ let count = Math.ceil(height / itemMainLength); '
                'return (count + 2 <= model.count) ? count + 2 : Math.min(count, model.count); }',
        })

    qcarousel.named_childs['path'] = create_carousel_path(qcarousel, elem)
    qcarousel.named_childs['delegate'] = create_carousel_delegate(qcarousel, elem)

    qcontainer.childs.append(qcarousel)
    return qcontainer


def create_systeminfo(elem: Element) -> QmlItem:
    qitem = create_text('system', elem)[0]
    qitem.props.update({
        'text': "root.model.get(currentIndex).games.count + ' GAMES AVAILABLE'",
        'readonly property alias currentIndex': 'root.currentIndex',
        'onCurrentIndexChanged': '{visible = false; opacity = 0.0; fadeInTimer.restart();}',
    })

    if 'pos' not in elem.params:
        qitem.props['anchors.top'] = "systemcarousel.bottom"

    if 'size' not in elem.params:
        qitem.props.update({
            'anchors.left': 'parent.left',
            'anchors.right': 'parent.right',
            'height': 'font.pixelSize * 1.75',
        })

    qtimer = QmlItem('Timer')
    qtimer.props = {
        'id': 'fadeInTimer',
        'interval': '1000',
        'onTriggered': '{parent.visible = true; parent.opacity = 1.0}',
    }

    qitem.childs.append(qtimer)
    qitem.extra_lines.append('Behavior on opacity { NumberAnimation { duration: 300 } }')

    return qitem
