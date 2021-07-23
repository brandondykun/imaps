# Tool created for the Institute for Mine Mapping, Archival Procedures, 
# and Safety (iMaps) at the Indiana University of Pennsylvania
# Created by Brandon Dykun
# 7/21/2021
# Requires ArcGIS Advanced License
# Requires Geostatistical Analyst and Spatial Analyst Extensions
#
# Explanation to come
#
#----------------------------------------------------------------------------------#
# Import system modules
import os
import arcpy 


class LicenseError(Exception):
    """Class to raise custom LicenseError."""
    pass

def create_out_path(file):
    """
    Creates proper path to the output geodatabse and
    proper naming convention for specified file(file).
    """
    return os.path.join(out_gdb, pad_num + '_' + file)

#------------------------------------Inputs---------------------------------------#
# Inputs formatted for use in the tool
out_gdb = arcpy.GetParameterAsText(0)
pad_num = arcpy.GetParameterAsText(1)
elev_pts = arcpy.GetParameterAsText(2)
in_dem = arcpy.GetParameterAsText(3)
pillars = arcpy.GetParameterAsText(4)

# Inputs formatted to be run while building tool
# out_gdb = 'C:/Users/Brandon/Desktop/imaps/project_data/CPA_AOI/Test_Outputs.gdb'                        # Output geodatabase
# pad_num = 'Pad15A'                                                                                      # Site Pad Number
# elev_pts = 'C:/Users/Brandon/Desktop/imaps/project_data/CPA_AOI/ConsolGasWellInfo.gdb/Pad15A_Contours'  # Elevation points                                                              # Pad Number for consistent naming convention
# in_dem = 'C:/Users/Brandon/Desktop/imaps/project_data/CPA_AOI/ConsolGasWellInfo.gdb/Pad15A_DEM1000ft'   # DEM
# pillars = 'C:/Users/Brandon/Desktop/imaps/project_data/CPA_AOI/ConsolGasWellInfo.gdb/Pad15A_Pillars'    # pillar polygons


#------------------------------------Inputs---------------------------------------#


#----------------------Extract Values to Points-----------------------------------#
# Name: ExtractValuesToPoints
# Description: Extracts a cell value from the DEM at each elevation point.
# This value is shown in the RASTERVALU field of the output point featureclass.
# Requirements: Spatial Analyst Extension, os module

# Set local variables
evp_in_pt_features = elev_pts   
evp_in_raster = in_dem         
evp_out_pt_features = create_out_path('Extract')                                                   
evp_interpolate_values = 'INTERPOLATE'
evp_add_attributes = 'VALUE_ONLY'

try:
    # Check out the ArcGIS Spatial Analyst extension license
    if arcpy.CheckExtension('Spatial') == 'Available':
        arcpy.CheckOutExtension('Spatial')
    else:
        raise LicenseError

    # Execute ExtractValuesToPoints
    arcpy.sa.ExtractValuesToPoints(evp_in_pt_features, evp_in_raster, 
                            evp_out_pt_features, evp_interpolate_values, 
                            evp_add_attributes)

    arcpy.AddMessage('Extract Values to Points completed successfully...')

except LicenseError:
    # Prints LicenseError
    print '*Spatial Analyst license is unavailable*'

except arcpy.ExecuteError:
    # Prints ExecuteError Message
    print arcpy.GetMessages(2)

finally:    
    # Checkin the ArcGIS Spatial Analyst extension license
    arcpy.CheckInExtension('Spatial')
#----------------------Extract Values to Points-----------------------------------#


#--------------------------------------IDW-----------------------------------------#
# Name: InverseDistanceWeighting
# Description: Interpolates the coal elevation point features onto a 
# rectangular raster using Inverse Distance Weighting (IDW).
# Requirements: Geostatistical Analyst Extension, os module

# Set local variables
idw_in_pt_features = create_out_path('Extract')                       
idw_z_field = 'ELEVATION'                                         # Make sure this will always be the same
idw_out_ga_layer = '' #optional                                                             
idw_out_raster = create_out_path('IDWElev')                             
idw_cell_size = ''                                                                  
idw_power = ''                                                                          

# Set variables for search neighborhood (OPTIONAL)
# If these are used, the idw_search_neighborhood = '' below 
# will need commented out
# idw_maj_semiaxis = ''                                          # Find standard settings for these
# idw_min_semiaxis = ''                                                                           
# idw_angle = ''                                                                                      
# idw_max_neighbors = ''                                                                              
# idw_min_neighbors = ''                                                                              
# idw_sector_type = ''                                                                      
# idw_search_neighbourhood = arcpy.SearchNeighborhoodStandard(idw_maj_semiaxis, idw_min_semiaxis,       
#                                                       idw_angle, idw_max_neighbors,
#                                                       idw_min_neighbors, idw_sector_type)
idw_search_neighborhood = ''
idw_weight_field = ''

try:
    # Check out the ArcGIS Geostatistical Analyst extension license
    if arcpy.CheckExtension('GeoStats') == 'Available':
        arcpy.CheckOutExtension('GeoStats')
    else:
        raise LicenseError

    # Execute IDW
    arcpy.IDW_ga(idw_in_pt_features, idw_z_field, idw_out_ga_layer,  
                    idw_out_raster, idw_cell_size, idw_power, 
                    idw_search_neighborhood, idw_weight_field)    

    arcpy.AddMessage('Inverse Distance Weighted completed successfully...')

except LicenseError:
    # Prints LicenseError
    arcpy.AddError('*Geostatistical Analyst license is unavailable*')

except arcpy.ExecuteError:
    # Prints ExecuteError Message
    print arcpy.AddError(2)

finally:    
    # Checkin the ArcGIS Geostatistical Analyst extension license
    arcpy.CheckInExtension('GeoStats')
    
#--------------------------------------IDW-----------------------------------------#


#--------------------------------Raster to Point-----------------------------------#
# Name: RasterToPoint
# Description: Converts the IWD raster dataset from the previous step 
# into point features. A point feature is created for every pixel in the raster.
# The elevation value for each point can be found in the grid_code field of the 
# created point feature class.
# Requirements: os module

# Set local variables
rtp_in_raster = create_out_path('IDWElev')                              
rtp_out_pt = create_out_path('IDWElev_Points')                       
rtp_field = ''                                                    # Find out if this needs to be here

try:
    # Execute RasterToPoint
    arcpy.RasterToPoint_conversion(rtp_in_raster, rtp_out_pt, rtp_field)

    arcpy.AddMessage('Raster to Point completed successfully...')

except arcpy.ExecuteError:
    # Prints ExecuteError Message
    print arcpy.GetMessages(2)
#--------------------------------Raster to Point-----------------------------------#


#-----------------------------------Add Field--------------------------------------#
# Name: AddField
# Description: Adds a new field named "DEPTH" to the featureclass 
# created in the Extract Values to Points step
# Requirements: os module

# Set local variables
af_in_features = create_out_path('Extract.shp')
af_field_name = 'DEPTH'
af_field_type = 'Float'
af_field_precision = 9
af_field_scale = 2
af_field_length = ''
af_field_alias = ''        # Find out is this needs any value
af_field_is_nullable = 'NULLABLE'

try:
    # Execute AddField 
    arcpy.AddField_management(af_in_features, af_field_name, 
                                af_field_type, af_field_precision, 
                                af_field_scale , af_field_length, 
                                af_field_alias, af_field_is_nullable)

except arcpy.ExecuteError:
    # Prints ExecuteError Message
    print arcpy.GetMessages(2)

#-----------------------------------Add Field--------------------------------------#


#---------------------------------Update Cursor------------------------------------#
# Name: UpdateCursor
# Description: Calculates a coal depth value (DEPTH) for each point by 
# subtracting coal elevation (Elevation) from ground elevation (RASTERVALU).
# Requirements: os module

# Set local variables
uc_fc = create_out_path('Extract')
uc_fields = ['DEPTH', 'RASTERVALU', 'ELEVATION']

try:
    # Create update cursor for feature class 
    with arcpy.da.UpdateCursor(uc_fc, uc_fields) as cursor:
        # For each row, calculates the DEPTH value 
        for row in cursor:
            row[0] = row[1] - row[2]
            
            # Update the cursor with the updated value
            cursor.updateRow(row)

except arcpy.ExecuteError:
    # Prints ExecuteError Message
    print arcpy.GetMessages(2)    

#---------------------------------Update Cursor------------------------------------#


#---------------------------------Spatial Join-------------------------------------#
# Name: SpatialJoin
# Description: Joins the attributes of IDW Elevation points created in the 
# Raster to Point step to the pillars shapefile based on spatial relationships.
# Requirements: os module

# Set local variables
sj_target_features = pillars    
sj_join_features = create_out_path('IDWElev_Points')
sj_outfc = create_out_path('Pillars_SpatialJoinIDW')
sj_join_operation = 'JOIN_ONE_TO_ONE'

try:
    #Run the Spatial Join tool, using the defaults 
    # for the join operation and join type
    arcpy.SpatialJoin_analysis(sj_target_features, sj_join_features, 
                                sj_outfc, sj_join_operation)

    arcpy.AddMessage('Spatial Join completed successfully...')

except arcpy.ExecuteError:
    # Prints ExecuteError Message
    print arcpy.GetMessages(2) 

#---------------------------------Spatial Join-------------------------------------#


