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

注意下面的参数中：

- gdb_end_point： 格式类似于gds-xxx.graphdb.rds.aliyuncs.com
- gdb_port：如果是使用GDB的内网地址，端口为8182；如果是公网地址，端口是3734


#### 删除所有的点

**也就是清空实例中所有的数据，`GDB`在删除点时也会删除相应的边**

```shell
python GdbDataRemover.py --host ${gdb_end_point} --port ${gdb_port} --username ${gdb_user} --password ${gdb_pwd}
```

#### 删除所有`Label`为`player`的点

```shell
python GdbDataRemover.py --host ${gdb_end_point} --port ${gdb_port} --username ${gdb_user} --password ${gdb_pwd} --label player
```

#### 删除所有的边

```shell
python GdbDataRemover.py --host ${gdb_end_point} --port ${gdb_port} --username ${gdb_user} --password ${gdb_pwd} --edge
```

#### 删除所有`Label`为`knows`的边

```shell
python GdbDataRemover.py --host ${gdb_end_point} --port ${gdb_port} --username ${gdb_user} --password ${gdb_pwd} --edge --label knows
```

## GdbLoader

工具发送`GDB`的导入请求，导入用户OSS数据到`GDB`实例，主要包括以下请求：

- 添加一个导入任务，导入OSS上CSV文件数据到GDB
- 获取GDB实例的导入任务列表
- 查询导入任务的详细信息，包括导入数据统计、错误信息等
- 删除一个导入任务，如果要求删除的任务正在运行，会先终止任务再删除

`GdbLoader`是GDB数据导入接口的简单封装，你可以作为参考集成到自己的项目中。

### 添加导入任务

```shell
python GdbLoader.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --todo add_task --source ${source} --arn ${ramRoleArn}

# or

python GdbLoader.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --todo add_task --source ${source} --ak ${accessKey} --sk ${secretKey}
```

### 查询导入任务

```shell
python GdbLoader.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --todo get_task --loaderId ${uuid}
```

### 删除导入任务

```shell
python GdbLoader.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --todo delete_task --loaderId ${uuid}
```

### 导入任务列表

```shell
python GdbLoader.py --host ${gdb_end_point} --username ${gdb_user} --password ${gdb_pwd} --todo list_task
```

