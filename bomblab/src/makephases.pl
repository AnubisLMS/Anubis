#!/usr/bin/perl 
use Getopt::Std;

############################################################################
# makephases.pl - Generates a phases.c file on stdout
#
# Copyright (c) 2002-2011, R. Bryant and D. O'Hallaron, All rights reserved.
############################################################################

$| = 1; # autoflush output on every print statement

#
# Some constant strings that are used in the phase declarations.
#
$MIN_BASE = 2;   # Min and max base values for various recursive sequences
$MAX_BASE = 4;  

#
# Some functions for generating random values that will be plugged 
# into the phase source files. 

# Return a letter from the alphabet
sub choose_letter 
{
    my (@list) = ("a" .. "z");
    return $list[rand(@list)];
}

# Return an integer in the range [50,1000]
sub choose_positive 
{
    return int(rand(951)) + 50;
}

# Return the sum of six integers in the range [1,16]
sub choose_sum_of_six 
{
    my (@array) = (2,
		   10,
		   6,
		   1,
		   12,
		   16,
		   9,
		   3,
		   4,
		   7,
		   14,
		   5,
		   11,
		   8,
		   15,
		   13);
    my ($sum) = 0;
    my ($i);
    my (@tmp);

    $sum_of_six_inv = "";

    for ($i=0; $i < 6; $i++) {
	$tmp[$i] = int(rand(16)); # index is [0,15]
	$sum += $array[$tmp[$i]];
	$tmp[$i] =~ s/10/:/; 
	$tmp[$i] =~ s/11/;/; 
	$tmp[$i] =~ s/12/</; 
	$tmp[$i] =~ s/13/=/; 
	$tmp[$i] =~ s/14/>/; 
	$tmp[$i] =~ s/15/?/; 
	$sum_of_six_inv = $sum_of_six_inv.$tmp[$i];
    }
    return $sum;
}

# Return a six-letter word
sub choose_short_word 
{
    my (@list) = ("devils", "flyers", "flames", "bruins", "sabres", "oilers"); 
    return $list[rand(@list)];
}

# Return an integer in the range [0,15]
sub choose_count_value 
{
    return int(rand(1)) + 15;
}

# Return some string
sub choose_some_string 
{
    my (@list) = ("When I get angry, Mr. Bigglesworth gets upset.",
		  "Crikey! I have lost my mojo!",
		  "He is evil and fits easily into most overhead storage bins.",
		  "When a problem comes along, you must zip it!",
		  "I turned the moon into something I call a Death Star.",
		  "Why make trillions when we could make... billions?",
		  "The moon unit will be divided into two divisions.",
		  "The future will be better tomorrow.",
		  "Public speaking is very easy.",
		  "Verbosity leads to unclear, inarticulate things.",
		  "I am not part of the problem. I am a Republican.",
		  "Houses will begat jobs, jobs will begat houses.",
		  "I am for medical liability at the federal level.",
		  "Wow! Brazil is big.",
		  "Brownie, you are doing a heck of a job.",
		  "There are rumors on the internets.",
		  "I was trying to give Tina Fey more material.",
		  "You can Russia from land here in Alaska.",
		  "I am the mayor. I can do anything I want.",
		  "We have to stand with our North Korean allies.",
		  "I can see Russia from my house!",
		  "All your base are belong to us.",
		  "I am just a renegade hockey mom.",
		  "And they have no disregard for human life.",
		  "Border relations with Canada have never been better.",
		  "For NASA, space is still a high priority.");
    return $list[rand(@list)];
}

# Return an integer in the range [2,9]
sub choose_place_in_list
{
    return int(rand(8)) + 2;
}

# Return a factorial in the range [4!,10!]
sub choose_factorial 
{
    my(@list) = (24, 120, 720, 5040, 40320, 362880, 3628800);    
    return $list[rand(@list)];
}

# Return a Fibonacci number in the range [F(9), ..., F(23)]
sub choose_fib_number 
{
    my (@list) = (55, 89, 144, 233, 377, 610, 987, 1597, 2584, 
		  4181, 6765, 10946, 17711, 28657, 46368);
    return $list[rand(@list)];
}

# Return a sequence index (n) in the range [5, ..., 9]
sub choose_seq_index 
{
    return int(rand(5)) + 5;
}

# Return a sequence base in the range [MIN_BASE, ..., MAX_BASE]
sub choose_seq_base 
{
    return int(rand($MAX_BASE - $MIN_BASE + 1)) + $MIN_BASE;
}

# Return a number from the geometric sequence [49, 120,..., 5764801]
sub choose_geom_number 
{
    my (@list) = (49, 343, 2401, 16807, 117649, 823543, 5764801);    
    return $list[rand(@list)];
}

# Return a number in the range [0,7]
sub choose_random_path
{
    return int(rand(8));
}

# Return sum of indexes in a binary search for over the range [0,14]
sub choose_search_sum
{
    my (@list) = (7, 10, 11, 13, 15, 19, 21, 18, 27, 35, 37, 31, 43, 45);
    return $list[rand(@list)];
}


##############
# Main routine
##############

# 
# Parse and check the command line arguments
#
getopts('hnd:i:u:w:p:');
if ($opt_h) {
    usage("");
}

# Is this a notifying custom bomb (default: no)
$notifying = $opt_n;

# Every bomb gets a positive integer bomb ID 
if (!$bomb_id) {
    $bomb_id = 0;
}
(($bomb_id = $opt_i) >= 0)
    or usage("Invalid bomb ID (-i)");

# Generic bombs cannot be compiled with notification
if ($bomb_id == 0 and $notifying) {
    usage("Generic bombs (-i  0) cannot notify (-n)");
}

# Arguments for custom (-i > 0) notifying (-n) bombs
if ($bomb_id > 0 and $notifying) {
    ($userid = $opt_u)
	or usage("Missing arg required for notifying custom bomb (-u)");
    ($user_password = $opt_w)
	or usage("Missing arg required for notifying custom bomb (-w)");
}

# If -p, use specific phase variants, otherwise use random variants
if ($opt_p) {
    @phases = split(//, $opt_p);
    ((@phases == 6) and (($opt_p =~ tr/a-c//) == 6)) 
	or usage("Invalid phase pattern (-p)");
} 
else {
    @list = ("a", "b", "c");
    for ($i=0; $i<6; $i++) {
	$phases[$i] = $list[rand(@list)];
    }
}
$phases[6] = ""; #secret phase

# Set the directory that contains the phase templates
$phasedir = $opt_d;
(-d $phasedir and -e $phasedir and -r $phasedir)
    or die "$0: ERROR: Could not read directory $phasedir\n";

#
# Emit the phases.c header
#
system("cat $phasedir/phasehead.c") == 0
    or die "$0: Could not read $phasedir/phasehead.c\n";

# 
# Emit the global definitions
#
printf("/* Global bomb ID */\n");
printf("int bomb_id = $bomb_id;\n\n");

# Only emit these for notifying bombs
if ($bomb_id > 0 and $notifying) {
    printf("/* Global userid */\n");
    printf("char userid[] = \"$userid\";\n\n");
    printf("/* Global user_password */\n");
    printf("char user_password[] = \"$user_password\";\n\n");
}
    
# 
# Emit the bomb phases
#
for ($i = 1; $i <= 7; $i++) {
    $infile = "$phasedir/phase$i$phases[$i-1].c";
    open(INFILE, $infile) 
	or die "$0: ERROR: could not open $infile: $!\n";

    # process each line in phase template
    while (<INFILE>) {
	$line = $_;

	# 
	# First we'll substitute any tags that need to be remembered
	# so that we can generate the solution.
	#
	if ($line =~ POSITIVE_SET) {
	    $positive = choose_positive();
	    $line =~ s/POSITIVE_SET/$positive/;
	}

	if ($line =~ SOME_STRING_SET) {
	    $some_string = choose_some_string();
	    $line =~ s/SOME_STRING_SET/$some_string/;
	}

	if ($line =~ FIB_NUMBER_SET) {
	    $fib_number = choose_fib_number();
	    $line =~ s/FIB_NUMBER_SET/$fib_number/;
	}

	if ($line =~ GEOM_NUMBER_SET) {
	    $geom_number = choose_geom_number();
	    $line =~ s/GEOM_NUMBER_SET/$geom_number/;
	}

	if ($line =~ FACTORIAL_SET) {
	    $factorial = choose_factorial();
	    $line =~ s/FACTORIAL_SET/$factorial/;
	}

	if ($line =~ SUM_OF_SIX_SET) {              # also remembers inverse
	    $sum_of_six = choose_sum_of_six();      # in $sum_of_six_inv
	    $line =~ s/SUM_OF_SIX_SET/$sum_of_six/;
	}

	if ($line =~ PLACE_IN_LIST_SET) {
	    $place_in_list = choose_place_in_list();
	    $line =~ s/PLACE_IN_LIST_SET/$place_in_list/;
	}

	if ($line =~ COUNT_VALUE_SET) {
	    $count_value = choose_count_value();
	    $line =~ s/COUNT_VALUE_SET/$count_value/;
	}

	if ($line =~ SHORT_WORD_SET) {
	    $short_word = choose_short_word();
	    $line =~ s/SHORT_WORD_SET/$short_word/;
	}

	if ($line =~ LETTER_SET) {
	    $letter = choose_letter();
	    $line =~ s/LETTER_SET/$letter/;
	}

	if ($line =~ RANDOM_PATH_SET) {
	    $random_path = choose_random_path();
	    $line =~ s/RANDOM_PATH_SET/$random_path/;
	}

	if ($line =~ SEQ_INDEX_SET) {
	    $seq_index = choose_seq_index();
	    $line =~ s/SEQ_INDEX_SET/$seq_index/;
	}

	if ($line =~ SEQ_BASE_SET) {
	    $seq_base = choose_seq_base();
	    $line =~ s/SEQ_BASE_SET/$seq_base/;
	}

	if ($line =~ SEARCH_SUM_SET) {
	    $search_sum = choose_search_sum();
	    $line =~ s/SEARCH_SUM_SET/$search_sum/;
	}


	# 
	# Next, we substitute any tags we remembered for the solution
	#
	$line =~ s/POSITIVE_GET/$positive/;
	$line =~ s/SOME_STRING_GET/$some_string/;
	$line =~ s/FIB_NUMBER_GET/$fib_number/;
	$line =~ s/GEOM_NUMBER_GET/$geom_number/;
	$line =~ s/FACTORIAL_GET/$factorial/;
	$line =~ s/PLACE_IN_LIST_GET/$place_in_list/;
	$line =~ s/COUNT_VALUE_GET/$count_value/;
	$line =~ s/SHORT_WORD_GET/$short_word/;
	$line =~ s/LETTER_GET/$letter/;
	$line =~ s/RANDOM_PATH_GET/$random_path/;
	$line =~ s/SEQ_INDEX_GET/$seq_index/;
	$line =~ s/SEQ_BASE_GET/$seq_base/;
	$line =~ s/SEARCH_SUM_GET/$search_sum/;

	# 
	# Next, we substitute tags whose inverses we 
	# remembered for solution
	#
	$line =~ s/SUM_OF_SIX_GET/$sum_of_six_inv/; 

	# 
	# Finally, we substitute any memoryless tags
	#
	$line =~ s/LETTER/choose_letter()/e;
	$line =~ s/POSITIVE/choose_positive()/e;
	$line =~ s/SUM_OF_SIX/choose_sum_of_six()/e;
	$line =~ s/COUNT_VALUE/choose_count_value()/e;
	$line =~ s/SOME_STRING/choose_some_string()/e;
	$line =~ s/PLACE_IN_LIST/choose_place_in_list()/e;
	$line =~ s/FACTORIAL/choose_factorial()/e;
	$line =~ s/FIB_NUMBER/choose_fib_number()/e;
	$line =~ s/GEOM_NUMBER/choose_geom_number()/e;
	$line =~ s/RANDOM_PATH/choose_random_path()/e;

	$line =~ s/MIN_BASE/$MIN_BASE/g;
	$line =~ s/MAX_BASE/$MAX_BASE/g;
	

	# Now output the modified line
	print "$line";
    }
    close(INFILE);
}

exit;

#
# End of main routine
#

#
# usage - print help message and terminate
#
sub usage 
{
    printf STDERR "$_[0]\n";
    printf STDERR "Usage: $0 [-hn] -d <dir> -i bombid [-u <userid> -p <phases>]\n";
    printf STDERR "Options:\n";
    printf STDERR "  -d <dir>     Directory of phase templates\n";
    printf STDERR "  -h           Print this message\n";
    printf STDERR "  -i <bombid>  Integer bomb ID (default: 0)\n";
    printf STDERR "  -n           Make notifying (default: non-notifying)\n";
    printf STDERR "  -p <phases>  Use specific [abc] phase variants (default: random)\n";
    printf STDERR "               e.g., '-p cababc' builds phases 1c, 2a, 3b, 4a, 5b, and 6c\n";
    printf STDERR "  -u <userid>  Userid (notifying bombs only)\n";
    printf STDERR "  -w <userpwd> User password (notifying bombs only)\n";
    die "\n";
}

