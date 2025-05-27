#!/bin/sh

PORT=8888

while true; do
  rm -f out
  mkfifo out

  cat out | nc -l $PORT > >(
    while read -r line; do
      [[ "$line" == $'\r' || -z "$line" ]] && break
    done
    {
      echo -e "HTTP/1.1 200 OK\r"
      echo -e "Content-Type: text/plain\r"
      echo -e "Connection: close\r"
      echo -e "\r"

      rand_int=$(od -vAn -N4 -tu4 < /dev/urandom | tr -d ' ')

      awk -v r="$rand_int" 'BEGIN { printf "%.10f\n", r/4294967295 }'
    } > out
  )
done
