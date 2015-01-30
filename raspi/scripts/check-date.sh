now_ns=`date +%s%N`
echo Date: `date`. Time offset with server \(incl. pssh latency\): $((($1 - $now_ns)/1000000))ms
