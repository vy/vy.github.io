reset

set terminal jpeg enhanced
set xlabel "# of switches"
set xtics 0,128,1024
set grid

set output "time.jpg"
set ylabel "start+shutdown time (minutes)"
set ytics 0,10,100

plot 'mininet-ovs.dat' using 1:($3/60.0) with points pointtype 7 title 'Open vSwitch', \
                    '' using 1:($3/60.0) smooth csplines title '', \
     'mininet-ref.dat' using 1:($3/60.0) with points pointtype 13 title 'Reference Implementation', \
                    '' using 1:($3/60.0) smooth csplines title ''

set output "memory.jpg"
set ylabel "memory usage (gigabytes)"
set ytics 0,2,32

# Note that while plotting the memory usage (that is, the 2nd field),
# we subtract the initial memory usage of the system at stale state
# from the results.

plot 'mininet-ovs.dat' using 1:(($2-590)/1024.0) with points pointtype 7 title 'Open vSwitch', \
                    '' using 1:(($2-590)/1024.0) smooth csplines title '', \
     'mininet-ref.dat' using 1:(($2-6464)/1024.0) with points pointtype 13 title 'Reference Implementation', \
                    '' using 1:(($2-6464)/1024.0) smooth csplines title ''
