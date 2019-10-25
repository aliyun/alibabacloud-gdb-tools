
# 打包

mvn package

目标文件 target/gdb-benchmark.tar.gz

# 配置

## config.json
exeCount：dsl执行次数

round：data.csv文件是否循环读取

## dsl.txt
存放一条待压测的dsl，变量使用$表示

## data.csv
存放待压测的数据，csv格式，顺序填充dsl中的"$"

## local.yaml
gremlin driver相关配置

# 运行
sh bin/start.sh ${压测线程数}