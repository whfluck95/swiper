#!/bin/bash

a=1234567890

# echo 与 printf 的区别
echo "=====$a======"
printf "=====$a======\n"

# 单引号、双引号的区别
echo '=====$a======'


if [ -d 'test.py' ]
then
    echo 'it is a dir'

elif [ -f 'test.py' ]
then
    echo 'it is a file'

else
    echo 'i dont know'
fi


for i in `seq 1 10`
do
    echo "current num is $i"
done


for ((i=0; i<10; i++))
do
    echo "current num is $i"
done
