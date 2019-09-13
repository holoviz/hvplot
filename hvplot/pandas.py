from . import patch

patch('pandas', extension='bokeh',
      exclude=['image', 'contour', 'contourf', 'quadmesh', 'rgb'])
