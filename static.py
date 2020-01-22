from enum import Enum, auto
from typing import Dict, Tuple, List


MAX_FORMAT_VERSION = 6


class PropType(Enum):
    NORMALIZED_PAIR = auto()
    NORMALIZED_RECT = auto()
    PATH = auto()
    STRING = auto()
    COLOR = auto()
    FLOAT = auto()
    BOOLEAN = auto()


KNOWN_ELEMENTS: Dict[str, Dict[str, PropType]] = {
    'image': {
        'pos': PropType.NORMALIZED_PAIR,
        'size': PropType.NORMALIZED_PAIR,
        'maxSize': PropType.NORMALIZED_PAIR,
        'origin': PropType.NORMALIZED_PAIR,
        'rotation': PropType.FLOAT,
        'rotationOrigin': PropType.NORMALIZED_PAIR,
        'path': PropType.PATH,
        'default': PropType.PATH,
        'tile': PropType.BOOLEAN,
        'color': PropType.COLOR,
        # 'colorEnd': PropType.COLOR,
        # 'gradientType': PropType.STRING,
        'visible': PropType.BOOLEAN,
        'zIndex': PropType.FLOAT,
    },
    # 'imagegrid': {
    #     'pos': PropType.NORMALIZED_PAIR,
    #     'size': PropType.NORMALIZED_PAIR,
    #     'margin': PropType.NORMALIZED_PAIR,
    #     'padding': PropType.NORMALIZED_RECT,
    #     'autoLayout': PropType.NORMALIZED_PAIR,
    #     'autoLayoutSelectedZoom': PropType.FLOAT,
    #     'gameImage': PropType.PATH,
    #     'folderImage': PropType.PATH,
    #     'imageSource': PropType.STRING,
    #     'scrollDirection': PropType.STRING,
    #     'centerSelection': PropType.BOOLEAN,
    #     'scrollLoop': PropType.BOOLEAN,
    #     'animate': PropType.BOOLEAN,
    #     'zIndex': PropType.FLOAT,
    # },
    # 'gridtile': {
    #     'size': PropType.NORMALIZED_PAIR,
    #     'padding': PropType.NORMALIZED_PAIR,
    #     'imageColor': PropType.COLOR,
    #     'backgroundImage': PropType.PATH,
    #     'backgroundCornerSize': PropType.NORMALIZED_PAIR,
    #     'backgroundColor': PropType.COLOR,
    #     'backgroundCenterColor': PropType.COLOR,
    #     'backgroundEdgeColor': PropType.COLOR,
    # },
    'text': {
        'pos': PropType.NORMALIZED_PAIR,
        'size': PropType.NORMALIZED_PAIR,
        'origin': PropType.NORMALIZED_PAIR,
        'rotation': PropType.FLOAT,
        'rotationOrigin': PropType.NORMALIZED_PAIR,
        'text': PropType.STRING,
        'backgroundColor': PropType.COLOR,
        'fontPath': PropType.PATH,
        'fontSize': PropType.FLOAT,
        'color': PropType.COLOR,
        'alignment': PropType.STRING,
        'forceUppercase': PropType.BOOLEAN,
        'lineSpacing': PropType.FLOAT,
        'value': PropType.STRING,
        'visible': PropType.BOOLEAN,
        'zIndex': PropType.FLOAT,
    },
    'textlist': {
        'pos': PropType.NORMALIZED_PAIR,
        'size': PropType.NORMALIZED_PAIR,
        'origin': PropType.NORMALIZED_PAIR,
        'selectorHeight': PropType.FLOAT,
        # 'selectorOffsetY': PropType.FLOAT,
        'selectorColor': PropType.COLOR,
        # 'selectorColorEnd': PropType.COLOR,
        # 'selectorGradientType': PropType.STRING,
        'selectorImagePath': PropType.PATH,
        'selectorImageTile': PropType.BOOLEAN,
        'selectedColor': PropType.COLOR,
        'primaryColor': PropType.COLOR,
        'secondaryColor': PropType.COLOR,
        'fontPath': PropType.PATH,
        'fontSize': PropType.FLOAT,
        # 'scrollSound': PropType.PATH,
        'alignment': PropType.STRING,
        'horizontalMargin': PropType.FLOAT,
        'forceUppercase': PropType.BOOLEAN,
        'lineSpacing': PropType.FLOAT,
        'zIndex': PropType.FLOAT,
    },
    # 'container': {
    #     'pos': PropType.NORMALIZED_PAIR,
    #     'size': PropType.NORMALIZED_PAIR,
    #     'origin': PropType.NORMALIZED_PAIR,
    #     'visible': PropType.BOOLEAN,
    #     'zIndex': PropType.FLOAT,
    # },
    # 'ninepatch': {
    #     'pos': PropType.NORMALIZED_PAIR,
    #     'size': PropType.NORMALIZED_PAIR,
    #     'path': PropType.PATH,
    #     'visible': PropType.BOOLEAN,
    #     'zIndex': PropType.FLOAT,
    # },
    'datetime': {
        'pos': PropType.NORMALIZED_PAIR,
        'size': PropType.NORMALIZED_PAIR,
        'origin': PropType.NORMALIZED_PAIR,
        'rotation': PropType.FLOAT,
        'rotationOrigin': PropType.NORMALIZED_PAIR,
        'backgroundColor': PropType.COLOR,
        'fontPath': PropType.PATH,
        'fontSize': PropType.FLOAT,
        'color': PropType.COLOR,
        'alignment': PropType.STRING,
        'forceUppercase': PropType.BOOLEAN,
        'lineSpacing': PropType.FLOAT,
        # 'value': PropType.STRING,  # undocumented
        'format': PropType.STRING,
        'displayRelative': PropType.BOOLEAN,
        'visible': PropType.BOOLEAN,
        'zIndex': PropType.FLOAT,
    },
    'rating': {
        'pos': PropType.NORMALIZED_PAIR,
        'size': PropType.NORMALIZED_PAIR,
        'origin': PropType.NORMALIZED_PAIR,
        'rotation': PropType.FLOAT,
        'rotationOrigin': PropType.NORMALIZED_PAIR,
        'color': PropType.COLOR,
        'filledPath': PropType.PATH,
        'unfilledPath': PropType.PATH,
        'visible': PropType.BOOLEAN,
        'zIndex': PropType.FLOAT,
    },
    # 'sound': {
    #     'path': PropType.PATH,
    # },
    # 'helpsystem': {
    #     'pos': PropType.NORMALIZED_PAIR,
    #     'origin': PropType.NORMALIZED_PAIR,
    #     'textColor': PropType.COLOR,
    #     'iconColor': PropType.COLOR,
    #     'fontPath': PropType.PATH,
    #     'fontSize': PropType.FLOAT,
    # },
    # 'video': {
    #     'pos': PropType.NORMALIZED_PAIR,
    #     'size': PropType.NORMALIZED_PAIR,
    #     'maxSize': PropType.NORMALIZED_PAIR,
    #     'origin': PropType.NORMALIZED_PAIR,
    #     'rotation': PropType.FLOAT,
    #     'rotationOrigin': PropType.NORMALIZED_PAIR,
    #     'default': PropType.PATH,
    #     'delay': PropType.FLOAT,
    #     'visible': PropType.BOOLEAN,
    #     'zIndex': PropType.FLOAT,
    #     'showSnapshotNoVideo': PropType.BOOLEAN,
    #     'showSnapshotDelay': PropType.BOOLEAN,
    # },
    # 'carousel': {
    #     'type': PropType.STRING,
    #     'size': PropType.NORMALIZED_PAIR,
    #     'pos': PropType.NORMALIZED_PAIR,
    #     'origin': PropType.NORMALIZED_PAIR,
    #     'color': PropType.COLOR,
    #     'colorEnd': PropType.COLOR,
    #     'gradientType': PropType.STRING,
    #     'logoScale': PropType.FLOAT,
    #     'logoRotation': PropType.FLOAT,
    #     'logoRotationOrigin': PropType.NORMALIZED_PAIR,
    #     'logoSize': PropType.NORMALIZED_PAIR,
    #     'logoAlignment': PropType.STRING,
    #     'maxLogoCount': PropType.FLOAT,
    #     'zIndex': PropType.FLOAT,
    # },
}

SUPPORTED_VIEWS = [
    'system',
    'basic',
    'detailed',
]

RESERVED_ITEMS: Dict[str, Dict[str, str]] = {
    'system': {
        'background': 'image',
        'logo': 'image',
        'logoText': 'text',
    },
    'basic': {
        'background': 'image',
        'logo': 'image',
        'logoText': 'text',
        'gamelist': 'textlist',
    },
    'detailed': {
        'background': 'image',
        'logo': 'image',
        'logoText': 'text',
        'gamelist': 'textlist',
        'md_image': 'image',
        'md_name': 'text',
        'md_description': 'text',
        'md_lbl_rating': 'text',
        'md_lbl_releasedate': 'text',
        'md_lbl_developer': 'text',
        'md_lbl_publisher': 'text',
        'md_lbl_genre': 'text',
        'md_lbl_players': 'text',
        'md_lbl_lastplayed': 'text',
        'md_lbl_playcount': 'text',
        'md_rating': 'rating',
        'md_releasedate': 'datetime',
        'md_developer': 'text',
        'md_publisher': 'text',
        'md_genre': 'text',
        'md_players': 'text',
        'md_lastplayed': 'datetime',
        'md_playcount': 'text',
    },
}

# These depend on data to display, and cannot be created as extra
RESTRICTED_TYPES: List[str] = [
    'datetime',
    'carousel',
    'imagegrid',
    'textlist',
]

FONT_SIZE_MINI: str = '0.03 * root.height'
FONT_SIZE_SMALL: str = '0.035 * root.height'
FONT_SIZE_MEDIUM: str = '0.045 * root.height'
FONT_SIZE_LARGE: str = '0.085 * root.height'

DEFAULT_ZORDERS: Dict[str, int] = {
    'background': 0,
    'gamelist': 20,
    'gamegrid': 20,
    'md_image': 30,
    'md_video': 30,
    'md_marquee': 35,
    'md_lbl_rating': 40,
    'md_lbl_releasedate': 40,
    'md_lbl_developer': 40,
    'md_lbl_publisher': 40,
    'md_lbl_genre': 40,
    'md_lbl_players': 40,
    'md_lbl_lastplayed': 40,
    'md_lbl_playcount': 40,
    'md_rating': 40,
    'md_releasedate': 40,
    'md_developer': 40,
    'md_publisher': 40,
    'md_genre': 40,
    'md_players': 40,
    'md_lastplayed': 40,
    'md_playcount': 40,
    'md_description': 40,
    'md_name': 40,
    'logoText': 50,
    'logo': 50,
    'systemcarousel': 40,
    'systemInfo': 50,
}

DEFAULT_PROPS: Dict[Tuple[str, str, str], Dict[str, str]] = {
    ('*', 'image', '*'): {
        'asynchronous': 'true',
        'visible': 'status == Image.Ready',
        'opacity': 'visible ? 1.0 : 0.0',
        'fillMode': 'Image.PreserveAspectFit',
        'smooth': 'false',
    },
    ('*', 'text', '*'): {
        'textFormat': 'Text.PlainText',
        'color': "'#000'",
        'horizontalAlignment': 'Text.AlignLeft',
        'verticalAlignment': 'Text.AlignVCenter',
        'font.family': 'es_default.name',
    },
    ('*', 'text', 'logoText'): {
        'text': 'modelData.name',
        'visible': '!logo.visible',
    },
    ('*', 'textlist', '*'): {
        'readonly property var currentGame': "model.get(currentIndex)",
        'focus': 'true',
        'highlightMoveDuration': '0',
        'readonly property int highlightHeight': f'{FONT_SIZE_MEDIUM} * 1.5',
        'preferredHighlightBegin': 'height * 0.5 - highlightHeight * 0.5',
        'preferredHighlightEnd': 'preferredHighlightBegin + highlightHeight',
        'highlightRangeMode': 'ListView.ApplyRange',
        'Keys.onPressed': 'if (!event.isAutoRepeat && api.keys.isAccept(event))'
                          ' { event.accepted = true; currentGame.launch(); }',
    },
    ('*', 'textlist', 'gamelist'): {
        'model': "modelData.games",
    },
    ('*', 'textlist__delegate', '*'): {
        'width': 'ListView.view.width',
        'elide': 'Text.ElideRight',
    },
    ('*', 'textlist__delegate', 'gamelist__delegate'): {
        'text': 'modelData.title',
    },
    ('*', 'rating', 'md_rating'): {
        'percentage': 'currentGame.rating',
    },
    ('*', 'text', 'md_description'): {
        'verticalAlignment': 'Text.AlignTop',
        'wrapMode': 'Text.WordWrap',
        'height': 'root.height - y',
    },
    ('*', 'helpsystem', '*'): {
        'x': '0.012 * root.width',
        'y': '0.9515 * root.height',
    },
    ('detailed', 'image', 'md_image'): {
        'x': 'root.width * 0.25',
        'y': 'gamelist.y + root.height * 0.2125',
        'source': 'currentGame.assets.boxFront',
        'smooth': 'true',
    },
    # ('detailed', 'image', 'md_marquee'): {
    #     'source': 'currentGame.assets.marquee',
    # },
}
DEFAULT_PROPS[('*', 'datetime', '*')] = {
    **DEFAULT_PROPS.get(('*', 'text', '*'), {}),
    **DEFAULT_PROPS.get(('*', 'datetime', '*'), {}),
}
DEFAULT_PROPS[('*', 'textlist__delegate', 'gamelist__delegate')] = {
    **DEFAULT_PROPS.get(('*', 'text', '*'), {}),
    **DEFAULT_PROPS.get(('*', 'textlist__delegate', 'gamelist__delegate'), {}),
}


def add_label_defaults():
    global DEFAULT_PROPS

    view = 'detailed'
    texts = {
        'md_name': "currentGame.title",
        'md_description': "currentGame.description",
        # TODO: release -> releaseDate
        'md_releasedate': "Qt.formatDateTime(currentGame.release, dateFormat) || 'unknown'",
        'md_developer': "currentGame.developer || 'unknown'",
        'md_publisher': "currentGame.publisher || 'unknown'",
        'md_genre': "currentGame.genre || 'unknown'",
        'md_players': "Helpers.format_players(currentGame.players)",
        'md_lastplayed': "Helpers.relative_date(currentGame.lastPlayed)",
        'md_playcount': "currentGame.playCount",
    }
    for key, text in texts.items():
        def_key = (view, RESERVED_ITEMS[view][key], key)
        DEFAULT_PROPS.setdefault(def_key, {})
        DEFAULT_PROPS[def_key]['text'] = text

    label_order = [
        'md_lbl_rating',
        'md_lbl_releasedate',
        'md_lbl_developer',
        'md_lbl_publisher',
        'md_lbl_genre',
        'md_lbl_players',
        'md_lbl_lastplayed',
        'md_lbl_playcount',
    ]
    for idx, label in enumerate(label_order):
        if idx == 0:
            label_x = '0.01 * root.width'
            label_y = '0.625 * root.height'
        elif idx == (len(label_order) / 2):
            def_key_first = (view, RESERVED_ITEMS[view][label_order[0]], label_order[0])
            label_x = '0.25 * root.width'
            label_y = DEFAULT_PROPS[def_key_first]['y']
        else:
            prev = label_order[idx - 1]
            label_x = f"{prev}.x"
            label_y = f"{prev}.y + {prev}.height"

        label_defaults = {
            'font.pixelSize': FONT_SIZE_SMALL,
            'x': label_x,
            'y': label_y,
        }
        def_key = (view, RESERVED_ITEMS[view][label], label)
        DEFAULT_PROPS[def_key] = {**DEFAULT_PROPS.get(def_key, {}), **label_defaults}

    for idx, label in enumerate(label_order):
        value = label.replace('_lbl', '')
        value_defaults = {
            'x': f"{label}.x + {label}.width",
            'y': f"{label}.y",
        }
        if value in texts:
            value_defaults['height'] = f"{label}.height"
            value_defaults['width'] = f"0.24 * root.width - {label}.width"
            value_defaults['font.pixelSize'] = f"{label}.font.pixelSize"
            value_defaults['elide'] = 'Text.ElideRight'
        if RESERVED_ITEMS[view][value] == 'rating':
            value_defaults['height'] = f"{label}.font.pixelSize"

        def_key = (view, RESERVED_ITEMS[view][value], value)
        DEFAULT_PROPS[def_key] = {**DEFAULT_PROPS.get(def_key, {}), **value_defaults}

    description_key = (view, 'text', 'md_description')
    DEFAULT_PROPS[description_key]['y'] = f'{label_order[-1]}.y + {label_order[-1]}.height + 0.01 * root.height'


add_label_defaults()


STATIC_FILES: Dict[str, str] = {
    '__components/SystemView.qml': '''
import QtQuick 2.0
import QtQuick.Window 2.2
FocusScope {
  id: root
  property alias model: logoAxis.model
  property alias currentIndex: logoAxis.currentIndex
  readonly property var g_PLATFORM_LOGOS: new Map([
    $$PLATFORM_LOGOS$$
  ])
  readonly property var g_PLATFORMS_WITH_SYSTEM_SCREEN: [
    $$PLATFORMS_WITH_SYSTEMS$$
  ]
  signal enter()
  enabled: focus
  Carousel {
    id: bgAxis
    anchors.fill: parent
    itemWidth: width
    model: root.model
    currentIndex: root.currentIndex
    highlightMoveDuration: 500
    delegate: Loader {
      width: PathView.view.width
      height: PathView.view.height
      asynchronous: true
      readonly property string sourceDir: {
        if (g_PLATFORMS_WITH_SYSTEM_SCREEN.includes(modelData.shortName)) return modelData.shortName;
        if (g_PLATFORMS_WITH_SYSTEM_SCREEN.includes('__generic')) return '__generic';
        return null;
      }
      source: (sourceDir && `../${sourceDir}/system.qml`) || 'MissingSystemView.qml'
    }
  }
  Rectangle {
    id: systemCarousel
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.verticalCenter: parent.verticalCenter
    height: 0.2325 * root.height
    color: '#d8ffffff'
    Carousel {
      id: logoAxis
      focus: true
      Keys.onPressed: {
        if (!event.isAutoRepeat && api.keys.isAccept(event)) {
          event.accepted = true;
          return root.enter();
        }
      }
      anchors.fill: parent
      itemWidth: width / 3
      delegate: Item {
        readonly property bool selected: PathView.isCurrentItem
        width: 0.25 * root.width
        height: 0.155 * root.height
        scale: selected ? 1.2 : 1.0
        opacity: selected ? 1.0 : 0.5
        Behavior on scale { NumberAnimation { duration: 200 } }
        Image {
          id: logoImage
          anchors.fill: parent
          asynchronous: true
          smooth: false
          readonly property string sourceRelPath: {
            let path = g_PLATFORM_LOGOS.get(modelData.shortName);
            if (path) return path;
            path = g_PLATFORM_LOGOS.get('__generic');
            if (path) return path
                .replace('${system.name}', modelData.shortName)
                .replace('${system.theme}', modelData.shortName);
            return null;
          }
          source: (sourceRelPath && `../${sourceRelPath}`) || ''
          fillMode: Image.PreserveAspectFit
          visible: status == Image.Ready
          opacity: visible ? 1.0 : 0.0
          Behavior on opacity { NumberAnimation { duration: 120 } }
        }
        Text {
          textFormat: Text.PlainText
          id: logoText
          anchors.centerIn: parent
          color: '#000'
          text: shortName || longName
          font.pixelSize: 0.085 * Window.height
          visible: logoImage.status != Image.Loading && logoImage.status != Image.Ready
        }
      }
    }
  }
  Text {
    textFormat: Text.PlainText
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.top: systemCarousel.bottom
    height: font.pixelSize * 1.75
    color: '#000'
    font.pixelSize: root.height * 0.035
    font.family: es_default.name
    text: root.model.get(root.currentIndex).games.count + " GAMES AVAILABLE"
    horizontalAlignment: Text.AlignHCenter
    verticalAlignment: Text.AlignVCenter
    Rectangle { anchors.fill: parent; color: '#ddd'; opacity: 0.847; z: -1 }
  }
}
''',
    '__components/DetailsView.qml': '''
import QtQuick 2.0
import QtQuick.Window 2.2
FocusScope {
  id: root
  property alias model: systemAxis.model
  property alias currentIndex: systemAxis.currentIndex
  readonly property var g_PLATFORMS_WITH_DETAILS_SCREEN: [
    $$PLATFORMS_WITH_DETAILS$$
  ]
  signal leave()
  Keys.onPressed: {
    if (!event.isAutoRepeat && api.keys.isCancel(event)) {
      event.accepted = true;
      return root.leave();
    }
  }
  Carousel {
    id: systemAxis
    focus: true
    anchors.fill: parent
    itemWidth: width
    delegate: Loader {
      width: systemAxis.width
      height: systemAxis.height
      asynchronous: true
      readonly property string sourceDir: {
        if (g_PLATFORMS_WITH_DETAILS_SCREEN.includes(modelData.shortName)) return modelData.shortName;
        if (g_PLATFORMS_WITH_DETAILS_SCREEN.includes('__generic')) return '__generic';
        return null;
      }
      source: (sourceDir && `../${sourceDir}/detailed.qml`) || 'MissingDetailedView.qml'
    }
  }
}
''',
    '__components/Carousel.qml': '''
import QtQuick 2.0
PathView {
  id: root
  property int itemWidth
  readonly property int pathWidth: pathItemCount * itemWidth
  signal itemSelected
  Keys.onLeftPressed: decrementCurrentIndex()
  Keys.onRightPressed: incrementCurrentIndex()
  Keys.onPressed: {
    if (!event.isAutoRepeat && api.keys.isAccept(event)) {
      event.accepted = true;
      itemSelected();
    }
  }
  snapMode: PathView.SnapOneItem
  preferredHighlightBegin: 0.5
  preferredHighlightEnd: 0.5
  pathItemCount: {
    let count = Math.ceil(width / itemWidth);
    return (count + 2 <= model.count) ? count + 2 : Math.min(count, model.count);
  }
  path: Path {
    startX: (root.width - root.pathWidth) / 2
    startY: root.height / 2
    PathLine {
      x: root.path.startX + root.pathWidth
      y: root.path.startY
    }
  }
}
''',
    # Note: small images with larger sourceSize and Tile fill didn't work well...
    '__components/RatingBar.qml': '''
import QtQuick 2.0
Item {
  id: root
  property real percentage
  property string filledPath
  property string unfilledPath
  Row {
    id: filledPart
    anchors { top: parent.top; bottom: parent.bottom; left: parent.left }
    width: root.width * percentage
    clip: true
    Repeater {
      model: 5
      Image {
        height: root.height
        width: height
        asynchronous: true
        source: filledPath
        smooth: false
      }
    }
  }
  Row {
    id: unfilledPart
    anchors { top: parent.top; bottom: parent.bottom; left: filledPart.right; right: parent.right }
    layoutDirection: Qt.RightToLeft
    clip: true
    Repeater {
      model: 5
      Image {
        height: root.height
        width: height
        asynchronous: true
        source: unfilledPath
        smooth: false
      }
    }
  }
}
''',
    'theme.qml': '''
import QtQuick 2.0
import '__components/'
FocusScope {
  id: root
  $$FONTLIST$$
  FontLoader { id: es_default; source: '__es_resources/opensans_hebrew_condensed_regular.ttf' }
  SystemView {
    id: systemView
    focus: true
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.bottom: parent.bottom
    height: parent.height
    model: api.collections
    onEnter: detailsView.focus = true
  }
  DetailsView {
    id: detailsView
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.top: systemView.bottom
    height: parent.height
    model: api.collections
    currentIndex: systemView.currentIndex
    onLeave: systemView.focus = true
    onCurrentIndexChanged: if (focus) systemView.currentIndex = currentIndex
  }
  states: [
    State {
      when: detailsView.focus
      AnchorChanges {
        target: systemView
        anchors.bottom: parent.top
      }
    }
  ]
  transitions: Transition {
    AnchorAnimation {
      duration: 400
      easing.type: Easing.OutQuad
    }
  }
}
''',
    '__components/helpers.js': '''
function format_players(count) {
    return count === 1
        ? count
        : "1\u2013" + count;
}
function relative_date(datetime) {
    if (isNaN(datetime))
        return "never";

    const now = new Date();
    const elapsed_ms = now.getTime() - datetime.getTime();

    const elapsed_hours = elapsed_ms / 1000 / 60 / 60;
    if (elapsed_hours < 24 && now.getDate() === datetime.getDate())
        return "today";

    const elapsed_days = Math.round(elapsed_hours / 24);
    if (elapsed_days <= 1)
        return "yesterday";

    return elapsed_days + " days ago";
}
''',
}
