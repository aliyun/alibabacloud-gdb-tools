
if [ -z $1 ]
then
    echo "param1 need thread count"
fi

java -cp "lib/*" "BenchMark" $1
