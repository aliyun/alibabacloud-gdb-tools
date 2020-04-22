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

Hints for parameters below：

- gdb_end_point： format looks like 'gds-xxx.graphdb.rds.aliyuncs.com'
- gdb_port：When use internal address，port is 8182；When use public address，port is 3734

#### Drop all vertices

```shell
python GdbDataRemover.py --host ${gdb_end_point} --port ${gdb_port} --username ${gdb_user} --password ${gdb_pwd}
```

#### Drop vertices with label `player`

```shell
python GdbDataRemover.py --host ${gdb_end_point} --port ${gdb_port} --username ${gdb_user} --password ${gdb_pwd} --label player
```

#### Drop all edges

```shell
python GdbDataRemover.py --host ${gdb_end_point} --port ${gdb_port} --username ${gdb_user} --password ${gdb_pwd} --edge
```

#### Drop edges with label `knows`

```shell
python GdbDataRemover.py --host ${gdb_end_point} --port ${gdb_port} --username ${gdb_user} --password ${gdb_pwd} --edge --label knows
```

## GdbLoader

A tool for GDB Loader which imports OSS data to GDB, it could make requests as follow:

- Add new task to import CSV file(s) on OSS to GDB
- Get the task list on GDB, return the task loaderId(uuid) list
- Get detail info of one task, include process records, errors
- Delete a task, it will stop the running task at first

This tool is just a simple shell of GDB OSS Loader, you could integrate it to your project as an example

### Add a new task

```shell
python GdbLoader.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --todo add_task --source ${source} --arn ${ramRoleArn}

# or

python GdbLoader.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --todo add_task --source ${source} --ak ${accessKey} --sk ${secretKey}
```

### Query the detail of task

```shell
python GdbLoader.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --todo get_task --loaderId ${uuid}
```

### Delete one task

```shell
python GdbLoader.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --todo delete_task --loaderId ${uuid}
```

### List all tasks

```shell
python GdbLoader.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --todo list_task
```
