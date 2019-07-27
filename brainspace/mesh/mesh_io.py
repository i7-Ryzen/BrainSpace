"""
High-level read/write functions for several formats.
"""

# Author: Oualid Benkarim <oualid.benkarim@mcgill.ca>
# License: BSD 3 clause


from vtkmodules.vtkIOPLYPython import vtkPLYReader, vtkPLYWriter
from vtkmodules.vtkIOXMLPython import vtkXMLPolyDataReader, vtkXMLPolyDataWriter
from vtkmodules.vtkIOLegacyPython import vtkPolyDataReader, vtkPolyDataWriter
from vtkmodules.vtkIOGeometryPython import (vtkSTLReader, vtkSTLWriter,
                                            vtkOBJReader, vtkOBJWriter)

from .io_support import (vtkFSReader, vtkFSWriter, vtkGIFTIReader,
                         vtkGIFTIWriter)
from ..vtk_interface.pipeline import serial_connect, get_output
from ..vtk_interface.decorators import wrap_output


# 'fs' type for FreeSurfer geometry data (also read FreeSurfer ascii as .asc)
supported_types = ['ply', 'stl', 'obj', 'vtp', 'vtk', 'asc', 'fs', 'gii']
supported_formats = ['binary', 'ascii']


@wrap_output
def _select_reader(itype):
    if itype == 'ply':
        reader = vtkPLYReader()
    elif itype == 'stl':
        reader = vtkSTLReader()
    elif itype == 'obj':
        reader = vtkOBJReader()
    elif itype == 'vtp':
        reader = vtkXMLPolyDataReader()
    elif itype == 'vtk':
        reader = vtkPolyDataReader()
    elif itype in ['asc', 'fs']:
        reader = vtkFSReader()
    elif itype == 'gii':
        reader = vtkGIFTIReader()
    else:
        raise TypeError('Unknown input type \'{0}\'.'.format(itype))
    return reader


@wrap_output
def _select_writer(otype):
    if otype == 'ply':
        writer = vtkPLYWriter()
    elif otype == 'stl':
        writer = vtkSTLWriter()
    elif otype == 'obj':
        writer = vtkOBJWriter()
    elif otype == 'vtp':
        writer = vtkXMLPolyDataWriter()
    elif otype == 'vtk':
        writer = vtkPolyDataWriter()
    elif otype in ['asc', 'fs']:
        writer = vtkFSWriter()
    elif otype == 'gii':
        writer = vtkGIFTIWriter()
    else:
        raise TypeError('Unknown output type \'{0}\'.'.format(otype))
    return writer


def load_surface(ipth, itype=None, return_data=True, update=True):
    """ Reads data.

    Parameters
    ----------
    ipth : str
        Input filename.
    itype : str, optional
        Input file type. If None, it is deduced from input filename.
        Default is None.
    return_data : bool, optional
        Whether to return data instead of filter. Default is False
    update : bool, optional
        Whether to update filter When return_data=True, filter is
        automatically updated. Default is True.

    Returns
    -------
    output : BSAlgorithm or BSPolyData
        Surface as a filter or BSPolyData.
    """

    if itype is None:
        itype = ipth.split('.')[-1]

    reader = _select_reader(itype)
    reader.filename = ipth

    return get_output(reader, update=update, as_data=return_data)


def save_surface(ifilter, opth, oformat=None, otype=None):
    """ Writes data.

    Parameters
    ----------
    ifilter : BSAlgorithm or BSDataObject
        Input filter or data.
    opth : str
        Output filename.
    oformat : {'ascii', 'binary'}, optional
        File format. Defaults to writer's default format.
        Only used when writer accepts format. Default is None.
    otype : str, optional
        File type. If None, type is deduced from output filename's extension.
        Default is None.

    """
    if otype is None:
        otype = opth.split('.')[-1]

    writer = _select_writer(otype)
    writer.filename = opth
    if otype not in ['vtp', 'tri', 'gii']:
        if oformat == 'ascii' or otype == 'asc':
            writer.filetype = 'ascii'
        else:
            writer.filetype = 'binary'

    serial_connect(ifilter, writer, update=True, as_data=False, port=None)


def convert_surface(ipth, opth, itype=None, otype=None, oformat=None):
    """Convert between file types.

    Parameters
    ----------
    ipth : str
        Input filename.
    opth : str
        Output filename.
    itype : str, optional
        Input file type. If None, type is deduced from input filename's
        extension. Default is None.
    otype : str, optional
        Output file type. If None, type is deduced from output filename's
        extension. Default is None.
    oformat : {'ascii', 'binary'}
        Output file format. Defaults to writer's default format.
        Only used when writer accepts format. Default is None.

    """
    reader = load_surface(ipth, itype=itype, return_data=False, update=False)
    save_surface(reader, opth, oformat=oformat, otype=otype)
