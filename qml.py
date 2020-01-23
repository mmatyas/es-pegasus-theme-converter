import os
from typing import Dict, List

from qml_render import render_view_items, font_path_to_name
from static import SUPPORTED_VIEWS, STATIC_FILES


def create_qml_defaults(default_views, out_files):
    for viewname in default_views:
        if viewname not in SUPPORTED_VIEWS:
            continue

        lines = render_view_items(viewname, None, default_views[viewname].values())

        import_lines = 5
        lines.insert(import_lines, "  Rectangle { anchors.fill: parent; color: '#fff' }")

        filepath = os.path.join('__components', 'Missing' + viewname.title() + 'View.qml')
        out_files[filepath] = '\n'.join(lines)


def create_qml_platform_views(platform, out_files):
    for viewname in platform.views:
        if viewname not in SUPPORTED_VIEWS:
            continue

        lines = render_view_items(viewname, platform.name, platform.views[viewname].values())

        filepath = os.path.join(platform.name, viewname + '.qml')
        out_files[filepath] = '\n'.join(lines)


def collect_fonts(ui_platforms):
    paths = []
    for platform in ui_platforms:
        for viewname in platform.views:
            for elem in platform.views[viewname].values():
                if 'fontPath' in elem.params:
                    paths.append(elem.params['fontPath'])

    paths = map(os.path.normpath, paths)
    paths = set(paths)
    paths = [{'name': font_path_to_name(p), 'path': p} for p in paths]
    return paths


def collect_platform_logos(ui_platforms):
    logos = {}
    for platform in ui_platforms:
        if 'system' not in platform.views:
            continue
        for elem in platform.views['system'].values():
            if elem.type == 'image' and elem.name == 'logo' and 'path' in elem.params:
                logos[platform.name] = elem.params['path']
    return logos


def collect_platform_views(ui_platforms) -> Dict[str, List[str]]:
    views: Dict[str, List[str]] = {}
    for platform in ui_platforms:
        pname = platform.name
        views[pname] = []
        for viewname in platform.views:
            views[pname].append(viewname)
    return views


def fill_templates(ui_platforms, out_files):
    fonts = collect_fonts(ui_platforms)
    platform_logos = collect_platform_logos(ui_platforms)
    platform_views = collect_platform_views(ui_platforms)

    def sorted_str(lines: List[str]) -> str:
        lines.sort()
        return '\n'.join(lines).strip()

    platform_logos_str = [f"    ['{platform}', '{path}']," for platform, path in platform_logos.items()]
    platform_logos_str = sorted_str(platform_logos_str)

    platforms_w_system_str = [f"    '{k}'," for k, views in platform_views.items() if 'system' in views]
    platforms_w_system_str = sorted_str(platforms_w_system_str)

    platforms_w_details_str = [f"    '{k}'," for k, views in platform_views.items() if 'detailed' in views]
    platforms_w_details_str = sorted_str(platforms_w_details_str)

    fontlist_str = [f"  FontLoader {{ id: {f['name']}; source: '{f['path']}' }}" for f in fonts]
    fontlist_str = sorted_str(fontlist_str)

    out_files['theme.qml'] = out_files['theme.qml'] \
        .replace('$$FONTLIST$$', fontlist_str)

    out_files['__components/DetailsView.qml'] = out_files['__components/DetailsView.qml'] \
        .replace('$$PLATFORMS_WITH_DETAILS$$', platforms_w_details_str)

    out_files['__components/SystemView.qml'] = out_files['__components/SystemView.qml'] \
        .replace('$$PLATFORM_LOGOS$$', platform_logos_str) \
        .replace('$$PLATFORMS_WITH_SYSTEMS$$', platforms_w_system_str)


def create_qml(theme_name, platforms, default_views) -> Dict[str, str]:
    out_files: Dict[str, str] = {}

    create_qml_defaults(default_views, out_files)
    for platform in platforms:
        create_qml_platform_views(platform, out_files)

    for path, contents in STATIC_FILES.items():
        out_files[path] = contents.strip()

    fill_templates(platforms, out_files)

    lines = [
        "name: " + theme_name,
    ]
    out_files['theme.cfg'] = '\n'.join(lines)

    return out_files
