# Alibaba Cloud Graph Database Service (GDB) Tools


## GdbDataRemover

As GDB supports transaction, all operation in a DSL execute in the same transaction. If simpely run `g.V().drop()` towards an instance with lots of data, the query will fail caused by limitation of transaction buffer.

`GdbDataRemover` supports two scenarios:

- Drop all data inside GDB
- Drop vertices with specified `Label` inside GDB

The tool wil drop data with limitation (default 500) speficied by user.

### Dependencies

`GdbDataRemover` depends on:
- gremlinpython
- argparse
- futures

The following command can be used to install all of them:
```shell
pip install -r requirements.txt --user
```

### Drop all vertices

```shell
python GdbDataRemover.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd}
```

### Drop vertices with label `player`

```shell
python GdbDataRemover.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --label player
```

### Drop all edges

```shell
python GdbDataRemover.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --edge
```

### Drop edges with label `knows`

```shell
python GdbDataRemover.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --edge --label knows
```
