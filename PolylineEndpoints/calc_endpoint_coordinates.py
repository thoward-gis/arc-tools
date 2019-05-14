"""
Tool Name: Calculate Endpoint Coordinates
Source: calc_endpoint_coordinates.py
Last Updated: April 19, 2019
Version: ArcGIS 10+ or ArcGIS Pro 1.0+

Required Arguments:
    Input Polyline Feature Class
Optional Arguments:
    Output Feature Class (should user want calculated fields be added to new copy of input)
"""

# import dependencies
import arcpy
import sys
import math
import traceback


def haversine(point1, point2):
    """
    Use Haversine formula to calculate great circle distance between two points (in meters).
    NOTE: accuracy +- 1-2%  since the earth is actually an oblate spheroid
    """
    lat1, long1 = point1
    lat2, long2 = point2
    diff_lat = math.radians(lat2 - lat1)
    diff_long = math.radians(long2 - long1)
    radius = 6378137  # earth radius in meters

    a = (math.sin(diff_lat/2) * math.sin(diff_lat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(diff_long/2) * math.sin(diff_long/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = c * radius
    return d


def find_distant_pts(allpts, beginpts, endpts, second_check=False):
    """
    Find two points in list that are furthest apart. Test distance only if more than one begin pt
    and one end pt.
    Ignore duplicates! If two endpoints are coincident, it is likely that is not true endpoint we're looking for.
    """
    beg = beginpts[0]
    end = endpts[0]
    biggest_distance = 0
    if len(allpts) > 2:
        for pt in allpts:
            if allpts.count(pt) == 1:
                for pt2 in allpts:
                    # don't consider duplicate (coincident) endpoints unless explicitly directed
                    if allpts.count(pt2) == 1 or second_check is True:
                        test_distance = haversine(pt, pt2)
                        if test_distance > biggest_distance:
                            biggest_distance = test_distance
                            if pt in beginpts:
                                beg = pt
                                end = pt2
                            else:
                                beg = pt2
                                end = pt
    return beg, end


def calc_endpoint_coord(in_polyline):
    """
    Add four fields to input feature class for X1, Y1, X2, Y2 (endpoints).
    Find begin and end vertices of any single or multipart polyline. If multipart polyline find the two
    endpoint vertices that are furthest apart using the Haversine formula. Make sure to ignore endpoints
    that are coincident because these are likely not the endpoints we are looking for.
    """
    # set names of new fields
    beginlat = "BegLat_Calc"
    beginlong = "BegLong_Calc"
    endlat = "EndLat_Calc"
    endlong = "EndLong_Calc"

    # add four fields for calculating begin/end lat/long
    field_list = [beginlat, beginlong, endlat, endlong]
    existing = [field.name for field in arcpy.ListFields(in_polyline)]
    field_error = False
    for f in field_list:
        if f not in existing:
            arcpy.AddField_management(in_polyline, f, "DOUBLE")
        else:
            arcpy.AddError("ERROR - field named {} already exists".format(f))
            field_error = True
    if field_error:
        sys.exit()

    # iterate thru each polyline feature using update cursor
    with arcpy.da.UpdateCursor(in_polyline, ['SHAPE@', beginlat, beginlong, endlat, endlong]) as cur:
        for row in cur:
            # find endpoints for each part in multipart line
            beginpts = [(part.getObject(0).Y, part.getObject(0).X) for part in row[0]]
            endpts = [(part.getObject(part.count - 1).Y, part.getObject(part.count - 1).X) for part in row[0]]
            # put all points in allpts list
            allpts = beginpts + endpts

            beg, end = find_distant_pts(allpts, beginpts, endpts)
            # if beg and end pts are the same, need to consider duplicates
            if beg == end:
                beg, end = find_distant_pts(allpts, beginpts, endpts, True)

            row[1] = beg[0]
            row[2] = beg[1]
            row[3] = end[0]
            row[4] = end[1]
            cur.updateRow(row)


if __name__ == '__main__':
    try:
        # Get parameters
        in_polyline = arcpy.GetParameterAsText(0)
        create_new = arcpy.GetParameterAsText(1)
        output_fc = arcpy.GetParameterAsText(2)
        # Create new output feature class if user specifies
        if create_new:
            in_polyline = arcpy.CopyFeatures_management(in_polyline, output_fc)
        # Calculate endpoint coordinates    
        calc_endpoint_coord(in_polyline)
        arcpy.AddMessage("Done!")
    
    except Exception as e:
        arcpy.AddError("ERROR! Unhandled exception! Exception: {}".format(str(e)))
