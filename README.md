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

### Submit the workflow 

``` bash
$ cd chess-qmb-workflow 
$ ./chess-qmb.py --execution_site sge
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

### Keep checking progress with `pegasus-status`. Once the workflow is done, display statistics with `pegasus-statistics`:

	$ pegasus-status [wfdir]
	$ pegasus-statistics [wfdir]
	...
 
