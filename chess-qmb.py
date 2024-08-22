#!/usr/bin/env python3
##!/usr/bin/python3

'''
Sample Pegasus workflow for doing processing data coming out of
CHESS Quantum Materials Beamline
https://github.com/keara-soloway/CHAPBookWorkflows
'''

import argparse
import logging
import os
import shutil
import sys
import json

from Pegasus.api import *

logging.basicConfig(level=logging.DEBUG)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# need to know where Pegasus is installed for notifications
PEGASUS_HOME = shutil.which('pegasus-version')
PEGASUS_HOME = os.path.dirname(os.path.dirname(PEGASUS_HOME))
CLUSTER_PEGASUS_HOME = "/nfs/chess/user/kvahi/software/pegasus/pegasus-5.0.7dev"
RUN_CONFIG= "run.config"

def build_site_catalog():
    '''
    Builds the Site Catalog that tells Pegasus what cluster layout looks like

    :return: the Site Catalog
    '''

    # --- Site Catalog -------------------------------------------------
    sc = SiteCatalog()

    # add a local site with an optional job env file to use for compute jobs
    shared_scratch_dir = "{}/local/scratch".format(BASE_DIR)
    local_storage_dir = "{}/local/storage".format(BASE_DIR)
    local = Site("local") \
        .add_directories(
        Directory(Directory.SHARED_SCRATCH, shared_scratch_dir)
        .add_file_servers(FileServer("file://" + shared_scratch_dir, Operation.ALL)),
        Directory(Directory.LOCAL_STORAGE, local_storage_dir)
        .add_file_servers(FileServer("file://" + local_storage_dir, Operation.ALL)))

    sc.add_sites(local)

    # add a sge site for CHESS SGE Cluster
    cluster_name = "sge"
    shared_scratch_dir = "{}/sge/scratch".format(BASE_DIR)
    local_storage_dir = "{}/sge/storage".format(BASE_DIR)
    sge = Site(cluster_name) \
        .add_directories(
        Directory(Directory.SHARED_SCRATCH, shared_scratch_dir)
        .add_file_servers(
            FileServer("file://" + shared_scratch_dir, Operation.ALL))) \
        .add_condor_profile(grid_resource="batch sge") \
        .add_pegasus_profile(
        style="glite",
        queue="all.q",
        data_configuration="nonsharedfs",
        auxillary_local="true",
        nodes=1,
        ppn=1,
        runtime=1800,
        clusters_num=2
    )
    sc.add_sites(sge)
    return sc

def generate_wf():
    '''
    Main function that parses arguments and generates the pegasus
    workflow
    '''

    parser = argparse.ArgumentParser(description="generate a CHESS QMB workflow")
    parser.add_argument('--execution-site', dest='execution_site', default="condorpool", required=False,
                        help='the site on which you want to run your workflows (condorpool|sge). defaults to condorpool')
    parser.add_argument('--raw-base-dir', dest='raw_base_dir', required=True,
                        help='the base directory where your raw cbf files are organized. This is the path to proj-name dir e.g. /nfs/chess/id4b/2024-1/ramshaw-3435-b')
    parser.add_argument('--calibration-base-dir', dest='calibration_base_dir', required=True,
                        help='the base directory where your calibration files are. The is path to the parent dir of the calibrations dir e.g. /nfs/chess/id4baux/2024-1/ramshaw-3435-b')
    args = parser.parse_args(sys.argv[1:])

    # pick up the run.config file
    config = json.load(open(RUN_CONFIG))
    
    wf = Workflow('chess-qmb')
    sc = build_site_catalog()
    tc = TransformationCatalog()
    rc = ReplicaCatalog()

    #name of the experiment, and run cycle
    #proj_name="ramshaw-3435-b"
    #run_cycle="2024-1"

    # pick up some qmb specific parameters from run.config
    specfile = config["specfile"]
    sample = config["sample"]
    scan_num = config["scan_num"]
    temperature = config["temperature"]

    # Where are those detector images?
    cbf_lfn_prefix = "raw6M/"+specfile+"/"+sample+"/"+temperature+"/"+specfile+"_"+str(scan_num).zfill(3)
    scan_dir=os.path.join(args.raw_base_dir, cbf_lfn_prefix)

    # Where are the calibrations files
    calibration_lfn_prefix = "calibrations"
    calibration_dir = os.path.join(args.calibration_base_dir, calibration_lfn_prefix)
    
    # --- Properties ----------------------------------------------------------
    
    # set the concurrency limit for the download jobs, and send some extra usage
    # data to the Pegasus developers
    props = Properties()
    props['pegasus.catalog.workflow.amqp.url'] = 'amqp://friend:donatedata@msgs.pegasus.isi.edu:5672/prod/workflows'
    props['pegasus.mode'] = 'development'
    #props['pegasus.data.configuration'] = 'nonsharedfs'
    props.write() 
    
    # --- Event Hooks ---------------------------------------------------------

    # get emails on all events at the workflow level
    wf.add_shell_hook(EventType.ALL, '{}/share/pegasus/notification/email'.format(PEGASUS_HOME))
    
    # --- Transformations -----------------------------------------------------

    stack_em_all_cbf = Transformation(
        'stack_em_all_cbf',
        site='sge',
        pfn=CLUSTER_PEGASUS_HOME + '/bin/pegasus-keg',
        is_stageable=False
    )
    tc.add_transformations(stack_em_all_cbf)

    simple_peakfinder = Transformation(
        'simple_peakfinder',
        site='sge',
        pfn=CLUSTER_PEGASUS_HOME + '/bin/pegasus-keg',
        is_stageable=False
    )
    tc.add_transformations(simple_peakfinder)

    auto_ormfinder = Transformation(
        'auto_ormfinder',
        site='sge',
        pfn=CLUSTER_PEGASUS_HOME + '/bin/pegasus-keg',
        is_stageable=False
    )
    tc.add_transformations(auto_ormfinder)

    pil6M_hkl_conv = Transformation(
        'pil6M_hkl_conv',
        site='sge',
        pfn=CLUSTER_PEGASUS_HOME + '/bin/pegasus-keg',
        is_stageable=False
    )
    tc.add_transformations(pil6M_hkl_conv)



    # --- Workflow -----------------------------------------------------
    # track the raw inputs for the workflow in the replica catalog.
    # we assume they are in the input directory
    executables_dir = os.path.join(BASE_DIR, "executables")

    # track all the scan files 
    scan_files=[]
    for fname in os.listdir(scan_dir):
        if fname[0] == '.':
            continue

        file_path = os.path.join(scan_dir, fname) 
        scan_file = File(cbf_lfn_prefix + "/" + fname)
        scan_files.append(scan_file)
        rc.add_replica("local", scan_file, file_path)  

    calibration_files=[]
    for fname in os.listdir(calibration_dir):
        if fname[0] == '.':
            continue

        file_path = os.path.join(scan_dir, fname)
        calibration_file = File(calibration_lfn_prefix + "/" + fname)
        calibration_files.append(calibration_file)
        rc.add_replica("local", calibration_file, file_path)
    
    # sanity check. make sure scan and calibration files were found
    if len(scan_files) == 0:
        logging.error("No scan files found in {}".format(scan_dir))
        sys.exit(1)

    if len(calibration_files) == 0:
        logging.error("No calibration files found in {}".format(calibration_dir))
        sys.exit(1)


    # stack_em_all_cbf job
    stack1_nxs = File("Stack1.nxs")
    stack2_nxs = File("Stack2.nxs")
    stack3_nxs = File("Stack3.nxs")
    stack_em_all_cbf_job = Job('stack_em_all_cbf', node_label="stack_em_all _cbf_2023")
    
    for calibration_file in calibration_files:
        stack_em_all_cbf_job.add_inputs(calibration_file)
        
    for scan_file in scan_files:
        stack_em_all_cbf_job.add_inputs(scan_file)

    stack_em_all_cbf_job.add_args("-o", stack1_nxs, stack2_nxs, stack3_nxs)
    stack_em_all_cbf_job.add_outputs(stack1_nxs, stack2_nxs, stack3_nxs, stage_out=True)
    wf.add_jobs(stack_em_all_cbf_job)

    # simple peakfinder job
    peaklist1_nxs = File("Peaklist1.nxs")
    simple_peakfinder_job = Job('simple_peakfinder', node_label="simple_peakfinder")
    simple_peakfinder_job.add_args("-a simple_peakfinder -T60 -i", stack1_nxs, "-o", peaklist1_nxs)
    simple_peakfinder_job.add_inputs(stack1_nxs)
    simple_peakfinder_job.add_outputs(peaklist1_nxs, stage_out=True)
    wf.add_jobs(simple_peakfinder_job)

    # auto orm finder job
    ormatrix_v1_nxs = File("ormatrix_v1.nxs")
    auto_ormfinder_job = Job('auto_ormfinder', node_label="auto_ormfinder")
    auto_ormfinder_job.add_args("-a auto_ormfinder -T60 -i", peaklist1_nxs, "-o", ormatrix_v1_nxs)
    auto_ormfinder_job.add_inputs(peaklist1_nxs)
    auto_ormfinder_job.add_outputs(ormatrix_v1_nxs, stage_out=True)
    wf.add_jobs(auto_ormfinder_job)

    # the mpil6M_hkl_conv job
    three_scans_hkli_nxs = File("3scans_HKLI.nxs")
    pil6M_hkl_conv_job = Job('pil6M_hkl_conv', node_label="pil6M_hkl_conv_3d_2023")
    pil6M_hkl_conv_job.add_inputs(ormatrix_v1_nxs, stack1_nxs, stack2_nxs, stack3_nxs)
    pil6M_hkl_conv_job.add_args("-a pil6M_hkl_conv -T60 -i")
    for file in [stack1_nxs, stack2_nxs, stack3_nxs, ormatrix_v1_nxs]:
        pil6M_hkl_conv_job.add_args(file)
    pil6M_hkl_conv_job.add_args("-o", three_scans_hkli_nxs)
    pil6M_hkl_conv_job.add_outputs(three_scans_hkli_nxs, stage_out=True)
    wf.add_jobs(pil6M_hkl_conv_job)

    # add dependencies explicitly to connect the j
    wf.add_dependency(simple_peakfinder_job, parents=[stack_em_all_cbf_job])
    wf.add_dependency(auto_ormfinder_job, parents=[simple_peakfinder_job])
    wf.add_dependency(pil6M_hkl_conv_job, parents=[auto_ormfinder_job, stack_em_all_cbf_job])
    
    try:
        wf.add_transformation_catalog(tc)
        wf.add_site_catalog(sc)
        wf.add_replica_catalog(rc)
        wf.write()
        wf.plan( sites=[args.execution_site], verbose=3, submit=True)
    except PegasusClientError as e:
        print(e.output)


if __name__ == '__main__':
    generate_wf()

