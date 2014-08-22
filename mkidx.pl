#!/usr/bin/perl -W
# $Id: mkidx.pl 23481 2014-03-28 20:52:24Z yanovich $

use Getopt::Std;
use strict;
use warnings;
use Symbol;

sub max {
	$_[0] < $_[1] ? $_[0] : $_[1];
}

my %opts;
getopts("c:k:L:", \%opts);
my $cv = $opts{c};
my $keylen = $opts{k};
my $lag = $opts{L} || 0;

my $pat = shift;
$pat = qr/$pat/;
my $outfn = "mkidx.out";
my $last_fn = "/";
my $pos;
my $fsz = -1;
my %fh;
my $nr = 0;
my @pos;
while (<>) {
	unless ($last_fn eq $ARGV) {
		$last_fn = $ARGV;
		$fsz = (stat ARGV)[7];
		$fsz = -1 unless $fsz;
		$pos = 0;
		@pos = ();
		print "\n" if $nr;
	}
	if (my ($mat) = m/$pat/) {
		$nr++;
		my $key = sprintf "%0${keylen}s", $mat;
		my $mat = sprintf "%${keylen}s", $mat;
		my $bkt = sprintf "%.${cv}s", $key;
		unless ($fh{$bkt}) {
			$fh{$bkt} = gensym;
			open $fh{$bkt}, "+>", "$outfn.$bkt" or
			    die "$outfn.$bkt: $!\n";
		}
		my $h = $fh{$bkt};
		print $h pack "a${keylen}Q", $mat, $pos;
		print "bad fid pos $pos\n" unless $mat;
		die "large key $mat at pos $pos\n" if length $mat > $keylen;
	}
	if ($. % 150000 == 0) {
		printf STDERR "\r%s: line %d, %d records (%.2f%%)",
		    $ARGV, $., $nr, int(10000*$pos/$fsz)/100,
	}
	push @pos, tell;
	$pos = shift @pos if @pos > $lag;
}

print "\n";

my $bkt;
for $bkt (keys %fh) {
	my $h = $fh{$bkt};
	seek $h, 0, 0 or die $!;

	print STDERR "sorting $bkt\n";

	my @v;
	my $len = $keylen+8;
	$/ = \$len;
	while (<$h>) {
		push @v, [ unpack "a${keylen}Q" ];
	}

	@v = sort { $a->[0] cmp $b->[0] } @v;

	seek $h, 0, 0 or die $!;

	for (@v) {
		print $h pack "a${keylen}Q", @{ $_ };
	}

	close $h;
}

print "done\n";
