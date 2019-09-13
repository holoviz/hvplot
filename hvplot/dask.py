from . import patch

patch('dask', extension='bokeh',
      exclude=['image', 'contour', 'contourf', 'quadmesh', 'rgb'])
