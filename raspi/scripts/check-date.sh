now_ns=`date +%s%N`
echo Uptime: `uptime | cut -d, -f1-2`. Time offset with server \(incl. pssh latency\): $((($1 - $now_ns)/1000000))ms
