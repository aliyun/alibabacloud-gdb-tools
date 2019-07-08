# 阿里云图数据库GDB工具

[**English Version of README**](README.md)

## GdbDataRemover

### 依赖安装

`GdbDataRemover` 依赖以下组件:
- gremlinpython
- argparse
- futures

执行下面的命令可以安装这些组件:
```shell
pip install -r requirements.txt --user
```

### 简介

`GDB`是支持事务的图数据库，单DSL中涉及的所有操作都会在同一个事务中完成。如果`GDB`实例中数据较多，简单地运行`g.V().drop()`会因为事务缓冲区大小的限制而失败。

`GdbDataRemover` 支持以下4种场景:

- 删除`GDB`中所有的点(包括对应的边)
- 删除`GDB`中指定`Label`的点(包括对应的边)
- 删除`GDB`中所有的边
- 删除`GDB`中指定`Label`的边

工具在删除数据时，会循环地发送请求，每个请求操作的元素个数在用户指定的限定之内(默认为`500`)。

#### 删除所有的点

**也就是清空实例中所有的数据，`GDB`在删除点时也会删除相应的边**

```shell
python GdbDataRemover.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd}
```

#### 删除所有`Label`为`player`的点

```shell
python GdbDataRemover.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --label player
```

#### 删除所有的边

```shell
python GdbDataRemover.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --edge
```

#### 删除所有`Label`为`knows`的边

```shell
python GdbDataRemover.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --edge --label knows
```
