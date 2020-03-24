#!/usr/bin/perl 
#!/usr/local/bin/perl 
use Getopt::Std;
use lib "..";
use Bomblab;

#######################################################################
# rtest - Bomb regression test
#
# Copyright (c) 2011, R. Bryant and D. O'Hallaron, All rights reserved.
#
# This program makes and tests <n> random non-notifying bombs
#
# Usage: $0 [-h]  [-n <num>] [-p <phases>]\n";
# Options:
#   -h           Print this message
#   -n <num>     Number of bombs to test (default 1)
#   -p <phases>  Make particular phases e.g., acbcbc
#
######################################################################

$| = 1; # autoflush output on every print statement

#
# usage - print help message and terminate
#
sub usage 
{
    printf STDERR "Usage: $0 [-h]  [-n <num>] [-p <phases>]\n";
    printf STDERR "Options:\n";
    printf STDERR "  -h           Print this message\n";
    printf STDERR "  -n <num>     Number of bombs to test (default 1)\n";
    printf STDERR "  -p <phases>  Make particular phases e.g., acbcbc\n";
    die "\n";
}

##############
# Main routine
##############

# 
# Parse and check the command line arguments
#
getopts('hn:p:');
if ($opt_h) {
    usage();
}

$iters = 1;
if ($opt_n and $opt_n < 1) {
    usage();
}
if ($opt_n) {
    $iters = $opt_n;
}

$phasearg = "";
if ($opt_p) {
    $phasearg = "-p $opt_p"; # make particular phases
}

# 
# Now make and test a bunch of random non-notifying bombs 
#
print "Testing $iters bombs ($Bomblab::CFLAGS).\n";
for ($i=1; $i <= $iters; $i++) {
    print ".";
    system("make cleanall  > /dev/null 2>&1");
    system("./makephases.pl -d phases -i 0 $phasearg > phases.c") == 0
	or die "\n$0: ERROR: makephases for bomb $i failed\n";

    system("export CFLAGS='$Bomblab::CFLAGS'; make -e bomb > /dev/null 2>&1") == 0
	or die "\n$0: ERROR: 'make bomb' for bomb $i failed\n";
    system("export CFLAGS='$Bomblab::CFLAGS'; make -e bomb-solve > /dev/null 2>&1") == 0
	or die "\n$0: ERROR: 'make bomb-solve' for bomb $i failed\n";
    system("make check-bomb > /dev/null 2>&1") == 0
	or die "\n$0: ERROR: Bomb $i exploded\n";
}	
print "\n$iters bombs checked out OK.\n";
exit;
