import freetype


class FontMetrics():
    def __init__(self, path: str):
        try:
            face = freetype.Face(path)
        except freetype.FT_Exception as err:
            raise RuntimeError(f"Error when trying to read the font file `{path}`: {err}")

        WINDOW_HEIGHT = 720
        SIZE_MEDIUM = 0.045
        face.set_pixel_sizes(0, int(WINDOW_HEIGHT * SIZE_MEDIUM))

        self.es_line_height = 0
        for i in range(32, 128):
            face.load_char(i)
            bitmap = face.glyph.bitmap
            self.es_line_height = max(self.es_line_height, bitmap.rows)

        face.load_char('S')
        s_rows = face.glyph.bitmap.rows

        es_s_bearing = face.glyph.metrics.horiBearingY / 64
        es_s_origin = (es_s_bearing + self.es_line_height) / 2
        self.es_s_y = es_s_origin - es_s_bearing
        self.es_baseline = self.es_s_y + s_rows

        qt_ascend = round(face.size.ascender / 64)
        qt_descend = round(-face.size.descender / 64)
        self.qt_line_height = qt_ascend + qt_descend
        self.qt_s_y = qt_ascend - s_rows
        self.qt_baseline = qt_ascend


class Font():
    def __init__(self, path: str):
        self.path = path
        self.metrics = FontMetrics(path)
