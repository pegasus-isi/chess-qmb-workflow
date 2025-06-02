# CHESS Quantum Beamline Processing Workflow
A Pegasus workflow to do processing for CHESS Quantum Materials Beamline

![CHESS Quantum Beamline Workflow](chess-qmb-workflow.png)

## Running the Sample Workflow on CHESS SGE Cluster

### Login to Classe

``` bash
$ ssh lnx201.classe.cornell.edu
$ cd ~/CLASSE_shortcuts/chess_[username]
$ git clone https://github.com/pegasus-isi/chess-qmb-workflow.git
```
### Check out the codes for the individual jobs


``` bash
$ cd chess-qmb-workflow
$ git clone https://gitlab01.classe.cornell.edu/ss3428/pegasus.git code
```
The above repository is in CLASSE GitLab and you need to do the checkout
using your Classe account.

### Science Configuration
The workflow science configuration is handled by a simple config file in json format named **run.config**

```json
{
    "proj_name": "hufnagel-3957-c",
    "run_cycle": "2024-3",
    "specfile": "FeNiCr",
    "sample": "bar_1",
    "start_scan_num": "23" ,
    "temperature": "25",
    "percofmax": "0.95",
    "min_braggs_peak": "300",
    "max_braggs_peak": "2000",
    "max_chisq": "0.08",
    "a": "3.569",
    "b": "3.569",
    "c": "3.569",
    "alpha": "90.0",
    "beta": "90.0",
    "gamma": "90.0"
}
```

This run.config is picked up by *chess-qmb.py* python script that is used to generate and submit the pegasus workflow.

### Submit the workflow 


``` bash
$ cd chess-qmb-workflow 
$ ./chess-qmb.py --execution_site sge --raw-base-dir /nfs/chess/id4b/2024-3/hufnagel-3957-c --calibration-base-dir /nfs/chess/id4baux/2024-3/hufnage
l-3957-c 
```

Note that when Pegasus plans/submits a workflow, a work directory is created and presented in the output. This directory is the handle to the workflow instance and used by Pegasus command line tools. Some useful tools to know about:

   * `pegasus-status -v [wfdir]`
        Provides status on a currently running workflow. ([more](https://pegasus.isi.edu/documentation/cli-pegasus-status.php))
   * `pegasus-analyzer [wfdir]`
        Provides debugging clues why a workflow failed. Run this after a workflow has failed. ([more](https://pegasus.isi.edu/documentation/cli-pegasus-analyzer.php))
   * `pegasus-statistics [wfdir]`
        Provides statistics, such as walltimes, on a workflow after it has completed. ([more](https://pegasus.isi.edu/documentation/cli-pegasus-statistics.php))
   * `pegasus-remove [wfdir]`
        Removes a workflow from the system. ([more](https://pegasus.isi.edu/documentation/cli-pegasus-remove.php))

During the workflow planning, Pegasus transforms the workflow to make it work well in the target execution environment.

The executable workflow has a set of additional tasks added by Pegasus: create scratch dir, data staging in and out, and data cleanup jobs.

### Check the status of the workflow:

	$ pegasus-status [wfdir]

You can keep checking the status periodically to see that the workflow is making progress.
You can add -w 60 option to the command to check the status every 60 seconds.

### Once the workflow is done, display statistics with `pegasus-statistics`:

	$ pegasus-statistics [wfdir]
	...
 
