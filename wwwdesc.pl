#! /usr/bin/perl -w
###################################################################################
#              Dan Cardamore <wombat@hld.ca>
#                   Copyright 2000 all rights reserved
#                   This software is released under the GNU GPL license
###################################################################################
# 	$rcs = ' $Id: wwwdesc.pl,v 1.2 2001/04/05 01:04:29 wombat Exp $ ' ;	
###################################################################################
use strict;
use CGI qw(param);
use DBI;
use POSIX ":sys_wait_h";
use File::stat;
use Date::Manip;
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

sub handleAll {
  my @files = get_files();
  foreach my $file (@files) 	{
	handleEntry($file);
  }
  return;
}

sub updateEntry($$) {
  my ($dbfile,$description) = @_;
  my $sth;
  my $results = &getEntry($dbfile);
  if (defined $results->[0]) {
	$sth=$dbh->prepare("UPDATE files set description=\'$description\'" .
						  "where name=\'$dbfile\'" );
  }
  else {
	$sth=$dbh->prepare("INSERT into files values(\'$dbfile\', \'0\', \'$description\')");
  }
  $sth->execute;
}

sub getEntry {
  my $dbfile = shift;

  my $sth = $dbh->prepare( "SELECT * FROM files where name=\'$dbfile\'" );
  $sth->execute;
  my @results = $sth->fetchrow_array;

  return \@results;
}

sub flagDirForThumbs {
  my ($dir, $size, $random, $thumbed) = @_;
  my $date = ParseDate("today");

  if ($thumbed == 1) {
	# just update the database to indicate that this directory has images as thumbs.
	# then we want to create all the thumbnails using "convert"
	opendir (DIR, $dir) or die $!;
	my @files = readdir(DIR);
	closedir (DIR);

	foreach my $file (@files) {
	  unless ( -f "$file") { next; }  # only look at files
	  if ( $file =~ /PAsmall/ ) { next; }  # ignore thumbnails.
	  if ( $file =~ /(png|gif|jpg|jpeg)$/i ) {
		`convert -geometry $size $file PAsmall$file`;
	  }
	}
  }

  my $sth = $dbh->prepare( "SELECT * FROM pictures where name=\'$dir\'" );
  $sth->execute;
  my @results = $sth->fetchrow_array;
  if (defined $results[0]) {
	$sth=$dbh->prepare("UPDATE pictures set size=\'$size\', random=\'$random\'," .
					   "thumbed=\'$thumbed\' where name=\'$dir\'");
  }
  else {
	$sth=$dbh->prepare("INSERT into pictures values(\'$dir\', \'$date\'," .
					   "\'$size\',\'$random\', \'$thumbed\')");
  }
  $sth->execute;
  return;
}

sub handleEntry {
  my ($file) = @_;
  if ($file eq "..") { return; }
  my $pwd = `pwd`;
  chomp $pwd;
  my $dbfile = relpath("$pwd" ."/$file");
  my $results = getEntry($dbfile);
  if (not defined $results->[2]) {
	$results->[2] = "";
  }
  print "--\n";
  print "$dbfile description was \"$results->[2]\"\n";
  print "$dbfile new description-> ";
  my $description = <STDIN>;
  chop $description;

  if ($description ne "") {
	updateEntry($dbfile, $description);
  }
  if (-d $dbfile) {
	# ask about the pictures
	print "Would you like this to be a thumbnailed page (y/n): ";
	my $thumbed = <STDIN>;
	chop $thumbed;
	if ($thumbed =~ 'y') {
	  # create the thumbs in this directory
	  print "What size would you like the thumbnails to be? (default: 80x80): ";
	  my $size = <STDIN>;
	  chop $size;
	  if ($size eq '') {
		$size = '80x80';
	  }

	  print "Would you like a random thumbnail to be displayed for this directory (y/n): ";
	  my $random = <STDIN>;
	  chop $random;
	  if ($random =~ 'y') {
		$random = 1;
		# flag this directory to have a random image popup
	  }
	  else { $random = 0; }

	  &flagDirForThumbs($dbfile, $size, $random, 1);
	}
	else {
	  &flagDirForThumbs($dbfile, "80x80", 0, 0);
	}
  }
  return;
}

sub relpath {
  my $file = shift;
  my $newfile = "";
  $file =~ s/\n//g;  # remove new lines
  my @peices = split /\//, $file;

  for (my $i = 0; $i <= $#peices; $i++)	{
	if ($peices[$i] eq '.') {
	  last;
	}
	if (defined $peices[$i+1] and $peices[$i + 1] eq "..")  {
	  last;
	}
	if ($peices[$i] ne ".")	{
	  $newfile .= "/$peices[$i]";
	}
  }
  $newfile =~ s/\/\//\//g;
  return $newfile;
}



##########################################################################
######################    MAIN    ########################################
##########################################################################

print "Updating descriptions for this directory\n";
print "Please enter your password for database user $dbuser: ";
$dbpass = <STDIN>;
chop $dbpass;
$dbh = DBI->connect("dbi:Pg:dbname=$dbname;host=$dbhost", "$dbuser", "$dbpass") or die $!;
handleAll();
$dbh->disconnect;
print "Done updates\n";
