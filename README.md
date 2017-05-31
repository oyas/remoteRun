remoteRun.py
------------

Run many tasks in remote servers.
You only type `remoteRun.py run`,
and this script copy your program data and run that in any of task runner servers.

## Help:

	$ remoteRun.py -h


## Role:

          User
           |
           |
      Front Server   <--(ssh)-- Master Server --(ssh)--> Task runner Servers
        (Global)                   (Local)                   (Local)
    User request receiver       Server Maneger              Calculator


## Usage:

**Step1**, rename `config.py.default` to `config.py`, write `config.py`, and copy it to Front server and Master server.

**Step2**, start `server.py` in Front server.

	$ server.py

**Step3**, start `run_server.py` in Master server.

	$ run_server.py

**Step4**, user run `remoteRun.py`, in Front server.

	$ remoteRun.py

User program name is `run.sh` in default.

**Step5**, check status of tasks.

	$ remoteRun.py status

Results is saved in `/tmp/remoteRun/` in Front server.

**Step6**, after running, pull result data.

	$ remoteRun.py pull [name]

