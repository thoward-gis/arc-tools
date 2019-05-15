"""
Tool Name: Validate Domain Values
Source: domain_valitdate.py
Last Updated: May 14, 2019
Version: ArcGIS 10+ or ArcGIS Pro 1.0+

Required Arguments:
    Input Feature Class

This script checks attribute values in all fields in a feature class to ensure they adhere to the workspace domains.
If errors are found, an ERROR_MESSAGE field is added to the input feature class where error messages are inserted.
"""
import arcpy
import os


def dict_of_domains(fc):
    """
    create dictionary from domains to use to check attribute values
    """
    domains = arcpy.da.ListDomains(os.path.dirname(fc))
    return {domain.name: domain.codedValues for domain in domains}


def validate_domains(fc, domain_dict):
    """ check all attribute values against domain value lists

    :param fc: Input feature class to check
    :param domain_dict: Dictionary object containing all domains and domain value lists
    """
    list_of_fields = arcpy.ListFields(fc)
    list_of_field_names = [field.name for field in list_of_fields]
    # add error field if necessary
    if "ERROR_MESSAGE" not in list_of_field_names:
        arcpy.AddField_management(fc, "ERROR_MESSAGE", field_type="TEXT", field_length=1000)
        list_of_field_names.append("ERROR_MESSAGE")

    # for field in list_of_fields:
    #     # check if field has domain
    #     if field.domain:
    with arcpy.da.UpdateCursor(fc, list_of_field_names) as cur:
        for row in cur:
            error_message = ''
            for idx in range(len(row)-1):
                # check if field has domain
                if list_of_fields[idx].domain:
                    if row[idx] not in domain_dict[list_of_fields[idx].domain].keys():
                        error_message += str(list_of_field_names[idx]) + " contains invalid value - " + str(row[idx]) + ", "
            if error_message:
                row[list_of_field_names.index("ERROR_MESSAGE")] = error_message
            else:
                row[list_of_field_names.index("ERROR_MESSAGE")] = None
            cur.updateRow(row)
        del cur  # get rid of any remaining locks


def del_error_field(fc, field="ERROR_MESSAGE"):
    """ delete ERROR_MESSAGE field - if no errors exist"""
    # find unique values list from field - ignore NULL, None values
    with arcpy.da.SearchCursor(fc, [field]) as cur:
        field_values = sorted({row[0] for row in cur if row[0]})
    if field_values:
        arcpy.DeleteField_management(fc, field)
        arcpy.AddMessage("No Domain Errors found! ERROR_MESSAGE field has been removed.")
    else:
        arcpy.AddMessage("Domain Errors Found! See ERROR_MESSAGE field added to input.")


#####################################################
################  MAIN  #############################

if __name__ == '__main__':
    try:
        # Get parameters
        in_fc = arcpy.GetParameterAsText(0)
        # create dictionary of domains
        domain_dic = dict_of_domains(in_fc)
        arcpy.AddMessage(domain_dic)
        # validate domains if domains exist
        if domain_dic:
            validate_domains(in_fc, domain_dic)
            # delete ERROR_MESSAGE field if no problems found
            del_error_field(in_fc)
        else:
            arcpy.AddMessage("The workspace selected does not contain any domains!")

        arcpy.AddMessage("Done!")

    except Exception as e:
        arcpy.AddError("ERROR! Unhandled exception! Exception: {}".format(str(e)))
