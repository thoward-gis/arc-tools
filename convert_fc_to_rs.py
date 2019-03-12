#-------------------------------------------------------------------------------
# Name:        convert_fc_to_rs
# Purpose:     No easy way to convert feature class to record set. This script converts
#              feature class to feature set then deletes geometry related keys
#              and then converts to record set.
#
# Author:      thoward
#
# Created:     03/12/2019
#-------------------------------------------------------------------------------

import arcpy
import json

def convert_fs_to_rs(dic):
    """
    convert FeatureSet to RecordSet by deleting 'geometry' related keys.
    forced to do this because arcpy.RecordSet() will not accept a feature class -OR- table view
    """
    if 'spatialReference' in dic:
        del dic['spatialReference']
    if 'geometryType' in dic:
        del dic['geometryType']
    for feat in dic['features']:
        if 'geometry' in feat:
            del feat['geometry']
    return dic


def create_recordset(fc):
    """
    create Record Set from Feature Class
    """
    arcpy.AddMessage("Creating record set...")
    fs = arcpy.FeatureSet(fc)
    # create dict so convert_fs_to_rs function will work
    dic = json.loads(fs.JSON)
    recset_text = json.dumps(convert_fs_to_rs(dic))
    # convert string to RecordSet object
    recset = arcpy.AsShape(recset_text, True)
    return recset
