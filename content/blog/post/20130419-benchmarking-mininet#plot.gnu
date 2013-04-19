reset

set terminal jpeg enhanced
set xlabel "# of switches"
set xtics 0,128,1024
set grid

set output "time.jpg"
set ylabel "start+shutdown time (minutes)"
set ytics 0,10,100

plot 'mininet.dat' using 1:($3/60.0) with points pointtype 7 title '', \
                '' using 1:($3/60.0) smooth csplines title ''

set output "memory.jpg"
set ylabel "memory usage (gigabytes)"
set ytics 0,2,32

plot 'mininet.dat' using 1:(($2-590)/1024.0) with points pointtype 1 title '', \
                '' using 1:(($2-590)/1024.0) smooth csplines title ''
