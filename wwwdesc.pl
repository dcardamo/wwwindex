#!/usr/bin/perl
###################################################################################
#              Dan Cardamore <wombat@hld.ca>
#                   Copyright 2000 all rights reserved
#                   This software is released under the GNU GPL license
###################################################################################
# 	$rcs = ' $Id: wwwdesc.pl,v 1.1 2001/01/24 03:36:30 wombat Exp $ ' ;	
###################################################################################
use strict;
use CGI qw(param);
use DBI;
use POSIX ":sys_wait_h";
use File::stat;
use vars qw/$dbname $dbhost $dbuser $dbpass $dbh/;

###################################################################################
##################   User Configuration Data          #############################
###################################################################################
# these are for connecting to the Postgres database
$dbname = 'wwwindex';
$dbhost = 'localhost';
$dbuser = 'wwwindex';

##################################################################################
###############  END OF CONFIGURATION DATA        ################################
##################################################################################


sub get_files {
	opendir (DIR, '.');
	my @allfiles = readdir(DIR);
	closedir (DIR);

	@allfiles = sort @allfiles;
	return @allfiles;
}

sub handleAll
{
		my @files = get_files();
		foreach my $file (@files)
		{
				handleEntry($file);
		}
		return;
}

sub updateEntry($$)
{
		my ($file,$description) = @_;
		my $pwd = `pwd`;
		chomp $pwd;
		$description = $dbh->quote($description);
		my $dbfile = relpath("$pwd" ."/$file");
				
		my $sth = $dbh->prepare( "UPDATE files set description='$description' where name='$dbfile'" );
		$sth->execute;
}

sub getEntry($)
{
		my $file = shift;
		my $pwd = `pwd`;
		chomp $pwd;
		my $dbfile = relpath("$pwd" ."/$file");
				
		my $sth = $dbh->prepare( "SELECT * FROM files where name='$dbfile'" );
		$sth->execute;
		my @results = $sth->fetchrow_array;

		return \@results;
}

sub handleEntry($)
{
		my ($file) = @_;
		if ($file eq "..") { return; }
		my $pwd = `pwd`;
		chomp $pwd;
		my $dbfile = relpath("$pwd" ."/$file");
		my $results = getEntry($file);
		print "------------------------------------\n";
		print "$dbfile WAS \"$results->[2]\"\n";
		print "$dbfile-> ";
		my $description = <STDIN>;
		chop $description;

		if ($description ne "")
		{
				updateEntry($file, $description);
		}
		return;
}

sub relpath($)
{
		my $file = shift;
		my $newfile = "";
		$file =~ s/\n//g;  # remove new lines
		my @peices = split /\//, $file;
		
		for (my $i = 0; $i <= $#peices; $i++)
		{
				if ($peices[$i + 1] eq "..")
				{
						last;
				}
				if ($peices[$i] ne ".")
				{
						$newfile .= "/$peices[$i]";
				}
		}
		$newfile =~ s/\/\//\//g;
		return $newfile;
}


print "Updating descriptions for this directory\n";
print "Please enter your password for database user $dbuser: ";
$dbpass = <STDIN>;
chop $dbpass;
$dbh = DBI->connect("dbi:Pg:dbname=$dbname;host=$dbhost", "$dbuser", "$dbpass") or die $!;
handleAll();
$dbh->disconnect;
print "Done updates\n";
