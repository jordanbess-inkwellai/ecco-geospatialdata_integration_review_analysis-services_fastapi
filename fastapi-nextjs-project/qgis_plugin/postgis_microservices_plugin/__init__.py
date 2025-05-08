# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PostGISMicroservices
                                 A QGIS plugin
 Integration with PostGIS Microservices and NextJS application
                             -------------------
        begin                : 2023-05-01
        copyright            : (C) 2023 by Your Name
        email                : your.email@example.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

def classFactory(iface):
    """Load PostGISMicroservices class from file PostGISMicroservices.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .postgis_microservices import PostGISMicroservices
    return PostGISMicroservices(iface)
