local_script_on_remote
=========

A substitute to ansible's `script` module. It was created when the module 
isn't working (always file not found on the server). I suspect that it's not working
because it doesn't automatically handle if the script's line-separator is \r\n. It doesn't automatically convert it,
so the shebang line will be "/usr/bin/sh\r" (note the trailing \r) or something else similar.

FAQ:
- #### Script file not found on the remote when running the script, even although `sudo cat SCRIPT_PATH` indicate script exists 
  is the directory is placed under `/root` directory? It has 700 permission.
  Check the permission of its parent and predecessors,
  even if the script file is 777 permission, if any of its upper-directories has more strict permission,
  the strict one will be used.

  Also check the shebang (hashbang) and see if it's setup correctly. Also check the shebang's line-separator. Make sure
  the shebang line is ended with "\n" instead of "\r\n".
- 



Requirements
------------

Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required.

Role Variables
--------------

A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
