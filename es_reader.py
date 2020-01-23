import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Set

from errors import print_info, print_error, warn
from es_items import Platform, Element, create_default_views
from property_types import parse_param, Property
from static import KNOWN_ELEMENTS, RESERVED_ITEMS, MAX_FORMAT_VERSION


def check_format_version(xml_path: str, root: ET.Element):
    node = root.find('formatVersion')
    if node is None:
        raise RuntimeError(f'{xml_path}: No <formatVersion> tag found')

    text = node.text.strip() if node.text else None
    if not text:
        warn(f"{xml_path}: The <formatVersion> is empty")
        return

    try:
        version = int(text)
    except ValueError:
        warn(f"{xml_path}: The <formatVersion> seems to be an invalid number")

    if version > MAX_FORMAT_VERSION:
        warn(f"{xml_path}: This theme may use features not yet supported")


def replace_variables(text, variables):
    var_pattern = re.compile('\\${(.+?)}')
    vars_handled_later = ['system.theme', 'system.name', 'system.fullName']

    var_match = var_pattern.search(text)
    while var_match:
        var_key = var_match.group(1)
        if var_key in vars_handled_later:
            var_match = var_pattern.search(text, pos=var_match.end())
            continue

        var_value = ''
        if var_key in variables:
            var_value = variables[var_key]

        text = text[:var_match.start()] + var_value + text[var_match.end():]
        var_match = var_pattern.search(text, pos=var_match.start() + len(var_value))

    return text


def parse_view_item_property(curr_dir: str, variables: Dict[str, str], itemtype: str, param: ET.Element) -> Property:
    if param.tag not in KNOWN_ELEMENTS[itemtype]:
        raise ValueError(f"Unknown or unsupported element parameter `{param.tag}` for `{itemtype}`")

    text = param.text.strip() if param.text else None
    if not text:
        raise ValueError(f"Empty element parameter `{param.tag}` for `{itemtype}`")

    text = replace_variables(text, variables)
    if not text:
        raise ValueError(f"After replacing the variables, `{param.tag}` for `{itemtype}` is empty")

    param_type = KNOWN_ELEMENTS[itemtype][param.tag]
    param_obj = parse_param(curr_dir, param_type, text)
    if param_obj is None:
        raise ValueError(f"Could not process element parameter `{param.tag}` "
                         f"for `{itemtype}` with value `{text}`")

    return param_obj


def read_view(xml_path, variables, viewname, viewnode, view) -> Set[str]:
    unsupported_elems = set()

    curr_dir = os.path.dirname(xml_path)

    # Example:
    # <view name="basic, detailed">
    #     <text name="md_lbl_rating, md_lbl_releasedate">
    #         <color>48474D</color>
    #     </text>
    # </view>

    for element in viewnode:
        if element.tag not in KNOWN_ELEMENTS:
            unsupported_elems.add(element.tag)
            continue

        if 'name' not in element.attrib:
            warn(f"{xml_path}: A `{element.tag}` element has no `name` field")
            continue

        affected_items = [s.strip() for s in re.split(r',\s*', element.attrib['name'])]
        affected_items = list(filter(None, affected_items))
        if not affected_items:
            warn(f"{xml_path}: A `{element.tag}` element's `name` field has no items")
            continue

        is_extra = 'extra' in element.attrib
        found_params: Dict[str, Property] = {}
        for param in element:
            try:
                found_params[param.tag] = parse_view_item_property(curr_dir, variables, element.tag, param)
            except ValueError as e:
                warn(f"{xml_path}: {e}")
                continue

        for itemname in affected_items:
            expected_type = RESERVED_ITEMS.get(viewname, {}).get(itemname)

            if expected_type and expected_type != element.tag:
                warn(f"{xml_path}: In `{viewname}` views `{itemname}` is a known element with type "
                     f"`{expected_type}`, but here it is declared as `{element.tag}`. "
                     "Ignoring the properties.")
                continue

            if is_extra and expected_type:
                warn(f"{xml_path}: In `{viewname}` views `{itemname}` is a known non-extra element, "
                     "but it is marked as an extra here. Ignoring the extra setting.")
            if not is_extra and not expected_type:
                warn(f"{xml_path}: In `{viewname}` views `{itemname}` is not a known element "
                     "and should be marked as extra, but it isn't. Marking it as one.")

            item = view.setdefault(itemname, Element(itemname, element.tag))
            assert(itemname == item.name)
            if item.type != element.tag:
                print_error(f"{xml_path}: A `{element.tag}` is defined with name `{itemname}`, "
                            f"but there's already an item called like that with type `{item.type}`. "
                            "Entry ignored.")
                continue

            item.params = {**item.params, **found_params}
            item.is_extra = not expected_type

    return unsupported_elems


def load_es_xml(xml_path: str) -> ET.Element:
    # ES supports illegal XMLs...
    try:
        with open(xml_path, 'r') as file:
            contents = file.read() \
                .replace('<!---', '<!-- ') \
                .replace('--->', ' -->')
            root = ET.fromstring(contents)
    except ET.ParseError as err:
        raise RuntimeError(f"{xml_path}: The file does not follow the rules of the XML format: {err}")
    except FileNotFoundError:
        raise RuntimeError(f"{xml_path}: File not found")
    except UnicodeDecodeError as err:
        raise RuntimeError(f"{xml_path}: Invalid unicode data: {err}")

    if root.tag != 'theme':
        raise RuntimeError(f"{xml_path}: A theme XML must start with a `<theme>` element")

    return root


def read_theme_xml(root_dir, xml_path, variables, views, check_version=True) -> Set[str]:
    # print_info(f'  - reading `{xml_path}`...')

    root = load_es_xml(xml_path)

    if check_version:
        check_format_version(xml_path, root)

    for node in root.findall('variables'):
        for child in node:
            text = child.text.strip() if child.text else None
            if text:
                variables[child.tag] = text

    all_unsupported_elems = set()

    for node in root.findall('include'):
        text = node.text.strip() if node.text else None
        if not text:
            warn(f"{xml_path}: Found an empty include")
            continue

        path = os.path.join(os.path.dirname(xml_path), text)
        unsupported_elems = read_theme_xml(root_dir, path, variables, views, check_version=False)
        all_unsupported_elems.update(unsupported_elems)

    feature_groups = [root] + root.findall('feature')
    for feature_group in feature_groups:
        for viewnode in feature_group.findall('view'):
            name_str = viewnode.attrib['name'] if viewnode.attrib and 'name' in viewnode.attrib else None
            if not name_str:
                continue

            affected_views = [s.strip() for s in re.split(r'[,\s]+', name_str)]
            affected_views = list(filter(None, affected_views))
            for viewname in affected_views:
                # TODO: Add support
                if viewname not in RESERVED_ITEMS:
                    continue
                views.setdefault(viewname, {})
                unsupported_elems = read_view(xml_path, variables, viewname, viewnode, views[viewname])
                all_unsupported_elems.update(unsupported_elems)

    # print_info(f'  - returning from `{xml_path}`...')
    return all_unsupported_elems


def find_theme_xmls(root_dir: str) -> Dict[str, str]:
    xml_filename = 'theme.xml'
    theme_xmls: Dict[str, str] = {}

    _, platform_dirs, root_files = next(os.walk(root_dir))

    for dirname in platform_dirs:
        theme_xml_path = os.path.join(root_dir, dirname, xml_filename)
        if os.path.isfile(theme_xml_path):
            theme_xmls[dirname] = theme_xml_path

    if xml_filename in root_files:
        theme_xmls['__generic'] = os.path.join(root_dir, xml_filename)

    return theme_xmls


def find_platforms(root_dir: str) -> List[Platform]:
    platforms: List[Platform] = []
    all_unsupported_elems: Set[str] = set()

    theme_xmls = find_theme_xmls(root_dir)
    for platform_name, xml_path in theme_xmls.items():
        print_info(f"Processing platform `{platform_name}` (`{xml_path}`)")

        try:
            variables: Dict[str, str] = {}
            views: Dict[str, Dict[str, Element]] = create_default_views(root_dir)
            unsupported_elems = read_theme_xml(root_dir, xml_path, variables, views)
        except RuntimeError as err:
            print_error(err)
            warn(f"Platform `{platform_name}` skipped")
            continue

        platforms.append(Platform(platform_name, views))
        all_unsupported_elems.update(unsupported_elems)

    if all_unsupported_elems:
        warn("The following unknown or unsupported items were found in this theme:")
        for elem in all_unsupported_elems:
            warn(f"  - {elem}")

    return platforms
