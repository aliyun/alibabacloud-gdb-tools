# Alibaba Cloud Graph Database Service (GDB) Tools

[**中文版 README**](README.cn.md)

## GdbDataRemover

### Dependencies

`GdbDataRemover` depends on:
- gremlinpython
- argparse
- futures

The following command can be used to install all of them:
```shell
pip install -r requirements.txt --user
```

### Summary

As GDB supports transaction, all operation in a DSL execute in the same transaction. If simpely run `g.V().drop()` towards an instance with lots of data, the query will fail caused by limitation of transaction buffer.

`GdbDataRemover` supports four scenarios:

- Drop all vertices inside GDB (Including related edges)
- Drop vertices with specified `Label` inside GDB (Including related edges)
- Drop all edges inside GDB
- drop edges with specified `Label` inside GDB

The tool wil drop data with limitation (default 500) speficied by user.

#### Drop all vertices

```shell
python GdbDataRemover.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd}
```

#### Drop vertices with label `player`

```shell
python GdbDataRemover.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --label player
```

#### Drop all edges

```shell
python GdbDataRemover.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --edge
```

#### Drop edges with label `knows`

```shell
python GdbDataRemover.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --edge --label knows
```
