"""The data each page shows, as frozen dataclasses.

A page template receives one of these and shows only what it holds, including every link. The
mockup gallery fills them with invented sample data; the real routes fill them from the database.
Because both use the same shapes, a page looks the same in the gallery and for real.
"""
