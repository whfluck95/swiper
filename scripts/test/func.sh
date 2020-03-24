echo '================'
echo '函数参数测试'
echo '================'

function foo() {
    echo "一共由 $# 个参数"
    echo "执行的命令是 $0"
    echo "第 1 个参数是 $1"
    echo "第 2 个参数是 $2"
    echo "第 3 个参数是 $3"
    echo "第 4 个参数是 $4"
    echo "全部参数：$@"
    echo "全部参数：$*"

    echo "遍历所有参数"
    for x in $*
    do
        echo "参数 $x"
    done
}

foo a1 a2 a3 a4

echo '================'
echo '脚本自身参数测试'
echo '================'

echo "一共由 $# 个参数"
echo "执行的命令是 $0"
echo "第 1 个参数是 $1"
echo "第 2 个参数是 $2"
echo "第 3 个参数是 $3"
echo "第 4 个参数是 $4"
echo "全部参数：$@"
echo "全部参数：$*"

echo "遍历所有参数"
for x in $*
do
    echo "参数 $x"
done
