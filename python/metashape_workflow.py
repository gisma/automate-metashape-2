# -*- coding: utf-8 -*-
# File for running a metashape workflow

# Derek Young and Alex Mandel
# University of California, Davis
# 2021

import sys

# ---- If this is a first run from the standalone python module, need to copy the license file from the full metashape install: from python import metashape_license_setup

## Define where to get the config file (only used if running interactively)
manual_config_file = "~/apps/Metashape_workflows/automate-metashape-2/config/base.yml"
# ---- If not running interactively, the config file should be supplied as the command-line argument after the python script, e.g.: python metashape_workflow.py config.yml


## Load custom modules and config file: slightly different depending whether running interactively or via command line
try:  # running interactively (in linux) or command line (windows)
    from python import metashape_workflow_functions as meta
    from python import read_yaml
except:  # running from command line (in linux) or interactively (windows)
    import metashape_workflow_functions as meta
    import read_yaml

if sys.stdin.isatty():
    config_file = sys.argv[1]
else:
    config_file = manual_config_file

## Parse the config file
cfg = read_yaml.read_yaml(config_file)

### Run the Metashape workflow

doc, log, run_id = meta.project_setup(cfg, config_file)

meta.enable_and_log_gpu(log, cfg)

if (cfg["photo_path"] != "") and (cfg["addPhotos"]["enabled"]):  # only add photos if there is a photo directory listed
    meta.add_photos(doc, cfg)

if cfg["calibrateReflectance"]["enabled"]:
    meta.calibrate_reflectance(doc, cfg)

if cfg["alignPhotos"]["enabled"]:
    meta.align_photos(doc, log, run_id, cfg)
    meta.reset_region(doc)

if cfg["filterPointsUSGS"]["enabled"]:
    meta.filter_points_usgs_part1(doc, log, cfg)
    meta.reset_region(doc)

if cfg["addGCPs"]["enabled"]:
    meta.add_gcps(doc, cfg)
    meta.reset_region(doc)

if cfg["optimizeCameras"]["enabled"]:
    meta.optimize_cameras(doc, log, run_id, cfg)
    meta.reset_region(doc)

if cfg["filterPointsUSGS"]["enabled"]:
    meta.filter_points_usgs_part2(doc, log, cfg)
    meta.reset_region(doc)

if cfg["buildDepthMaps"]["enabled"]:
    meta.build_depth_maps(doc, log, cfg)

if cfg["buildPointCloud"]["enabled"]:
    meta.build_point_cloud(doc, log, run_id, cfg)

if cfg["buildModel"]["enabled"]:
    meta.build_model(doc, log, run_id, cfg)

# For this step, the check for whether it is enabled in the config happens inside the function, because there are two steps (DEM and ortho), each of which can be enabled independently
meta.build_dem_orthomosaic(doc, log, run_id, cfg)

if cfg["photo_path_secondary"] != "":
    meta.add_align_secondary_photos(doc, log, run_id, cfg)

meta.export_report(doc, run_id, cfg)

meta.finish_run(log, config_file)
