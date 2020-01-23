from typing import Dict, Tuple
from property_types import parse_param, Property
from static import KNOWN_ELEMENTS


class Platform():
    def __init__(self, name, views):
        self.name = name
        self.views = views


class Element():
    def __init__(self, name, typename):
        self.name = name
        self.type = typename
        self.is_extra = False
        self.params: Dict[str, Property] = {}

    def __repr__(self):
        return f"{self.type} {self.name}, is_extra={self.is_extra}, params=[{','.join(self.params)}]"


DEFAULT_VIEW_ITEMS: Dict[str, Dict[str, str]] = {
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


FONT_SIZE_MINI: str = '0.03'
FONT_SIZE_SMALL: str = '0.035'
FONT_SIZE_MEDIUM: str = '0.045'
FONT_SIZE_LARGE: str = '0.085'


DEFAULT_PROPS: Dict[Tuple[str, str, str], Dict[str, str]] = {
    ('*', '*', '*'): {
    },
    ('*', 'image', '*'): {
    },
    ('*', 'text', '*'): {
        'fontSize': FONT_SIZE_MEDIUM,
        'forceUppercase': 'false',
        'color': '000000',
        'alignment': 'left',
        'lineSpacing': '1.5',
    },
    ('*', 'datetime', '*'): {
        'displayRelative': 'false',
        'format': '%Y-%m-%d',
    },
    ('*', 'image', 'background'): {
        'size': '1 1',
    },
    ('*', 'image', 'logo'): {
        'size': '0 0.185',
        'origin': '0.5 0',
        'pos': '0.5 0',
    },
    ('*', 'text', 'logoText'): {
        'pos': '0 0',
        'size': '1 0',
        'alignment': 'center',
    },
    ('*', 'textlist', '*'): {
        'selectorColor': '000000',
        'selectedColor': '000000',  # full alpha?
        'primaryColor': '0000ff',
        'secondaryColor': '00ff00',
        'alignment': 'center',
        'horizontalMargin': '0',
        'forceUppercase': 'false',
        'lineSpacing': '1.5',
        'selectorHeight': str(float(FONT_SIZE_MEDIUM) * 1.5),
        'selectorOffsetY': '0',
    },
    ('*', 'rating', '*'): {
        'filledPath': "__es_resources/star_filled.svg",
        'unfilledPath': "__es_resources/star_unfilled.svg",
        'percentage': '0.5',
    },
    ('basic', 'textlist', 'gamelist'): {
        'pos': '0 0.2',
        'size': '1 0.8',
    },
    ('detailed', 'textlist', 'gamelist'): {
        'pos': '0.51 0.2',
        'size': '0.49 0.8',
        'alignment': 'left',
    },
    ('detailed', 'image', 'md_image'): {
        'origin': '0.5 0.5',
        'maxSize': '0.48 0.4',
    },
    ('detailed', 'text', 'md_name'): {
        'pos': '1 1',
        'color': 'aaaaaa',
        'alignment': 'center',
    },
    ('detailed', 'text', 'md_description'): {
        'pos': '0.1 0.65',
        'size': '0.48 0',
        'fontSize': FONT_SIZE_SMALL,
    },
    ('detailed', 'text', 'md_lbl_rating'): {
        'text': "Rating: ",
        'fontSize': FONT_SIZE_SMALL,
    },
    ('detailed', 'text', 'md_lbl_releasedate'): {
        'text': "Released: ",
        'fontSize': FONT_SIZE_SMALL,
    },
    ('detailed', 'text', 'md_lbl_developer'): {
        'text': "Developer: ",
        'fontSize': FONT_SIZE_SMALL,
    },
    ('detailed', 'text', 'md_lbl_publisher'): {
        'text': "Publisher: ",
        'fontSize': FONT_SIZE_SMALL,
    },
    ('detailed', 'text', 'md_lbl_genre'): {
        'text': "Genre: ",
        'fontSize': FONT_SIZE_SMALL,
    },
    ('detailed', 'text', 'md_lbl_players'): {
        'text': "Players: ",
        'fontSize': FONT_SIZE_SMALL,
    },
    ('detailed', 'text', 'md_lbl_lastplayed'): {
        'text': "Last played: ",
        'fontSize': FONT_SIZE_SMALL,
    },
    ('detailed', 'text', 'md_lbl_playcount'): {
        'text': "Times played: ",
        'fontSize': FONT_SIZE_SMALL,
    },
    ('detailed', 'datetime', 'md_lastplayed'): {
        'displayRelative': 'true',
    },
}
DEFAULT_PROPS[('*', 'datetime', '*')] = {
    **DEFAULT_PROPS[('*', 'text', '*')],
    **DEFAULT_PROPS[('*', 'datetime', '*')],
}


def create_default_views(root_dir: str) -> Dict[str, Dict[str, Element]]:
    views: Dict[str, Dict[str, Element]] = {}
    for viewname in DEFAULT_VIEW_ITEMS:
        views[viewname] = {}

        for itemname, itemtype in DEFAULT_VIEW_ITEMS[viewname].items():
            prop_keys = [
                ('*', '*', '*'),
                ('*', itemtype, '*'),
                (viewname, itemtype, '*'),
                ('*', itemtype, itemname),
                (viewname, itemtype, itemname),
            ]
            str_props: Dict[str, str] = {}
            for key in prop_keys:
                str_props.update(DEFAULT_PROPS.get(key, {}))

            views[viewname][itemname] = Element(itemname, itemtype)
            for propname, propval in str_props.items():
                proptype = KNOWN_ELEMENTS[itemtype].get(propname)
                if not proptype:
                    # every item has some basic properties, but some of them
                    # cannot be set (eg. rotation for many types)
                    continue

                prop = parse_param(root_dir, proptype, propval)
                assert(prop is not None)
                views[viewname][itemname].params[propname] = prop

    return views
