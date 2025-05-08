def classFactory(iface):
    """
    Load PostGISMicroservicesPlugin class
    
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .main import PostGISMicroservicesPlugin
    return PostGISMicroservicesPlugin(iface)
