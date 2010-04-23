# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

def main():
    import os

    GOOGLE_MERCATOR = """# Google Mercator
<900913> +proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs <>
"""

    minitage_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../../..')
    epsg_filepath = os.path.join(minitage_dir, 'dependencies/proj-4.6/parts/part/share/proj/epsg')

    epsg_file = open(epsg_filepath, mode='a+')
    try:
        if GOOGLE_MERCATOR not in epsg_file.read():
            epsg_file.write(GOOGLE_MERCATOR)
    finally:
        epsg_file.close()

if __name__ == "__main__":
    main()
