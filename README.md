# hcl

Explore **H**df5 files on the **C**ommand **L**ine.

Designed to be familiar to Unix CLI users, but no particular effort has been made for true compatibility or POSIX compliance.

## Usage

```_help
usage: hcl [-h] [-c COMMAND] [-p PLUGIN] [--verbose] [--mode MODE] [file]

CLI for interactive exploration of HDF5 files.

positional arguments:
  file                  HDF5 file to explore. Add ':/path/to/group' to start
                        in a specific group.

optional arguments:
  -h, --help            show this help message and exit
  -c COMMAND, --command COMMAND
                        Run a single command and exit.
  -p PLUGIN, --plugin PLUGIN
                        Import path for additional commands. Imported object
                        can be a Command subclass, an iterable of them, or a
                        callable returning either. Format
                        '{absolute_module}:{object}'. Can be used multiple
                        times.
  --verbose, -v         Increase logging verbosity, up to -vv for debug.
  --mode MODE, -m MODE  Mode in which to open the file. 'r' (default):
                        Readonly, file must exist. 'r+': Read/write, file must
                        exist. 'w': Create file, truncate if exists. 'w-' or
                        'x': Create file, fail if exists. 'a': Read/write if
                        exists, create otherwise.
```

### Commands available

```_commands
attrs               List attributes or look at one attribute.
cd                  Change working group.
chunks              Get dataset chunks.
compression         Get dataset compression.
compression_opts    Get dataset compression_opts.
driver              Get group or dataset driver.
dtype               Get dataset dtype.
exit                Quit hcl.
filename            Get group or dataset filename.
fillvalue           Get dataset fillvalue.
fletcher32          Get dataset fletcher32.
help                List available commands.
is_virtual          Get dataset is_virtual.
libver              Get group or dataset libver.
ls                  List members of a group.
maxshape            Get dataset maxshape.
mode                Get group or dataset mode.
name                Get group or dataset name.
pwd                 Get working group.
scaleoffset         Get dataset scaleoffset.
shape               Get dataset shape.
shuffle             Get dataset shuffle.
size                Get dataset size.
tree                Show hierarchy as a tree.
userblock_size      Get group or dataset userblock_size.
```

See files in [commands/](./commands) for usage for each command.

## Notes

Very similar to [h5cli](https://pypi.org/project/h5cli/).
`hcl` features more documentation, piping output from `--command` mode, and doesn't crash when I try to run it.
