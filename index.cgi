#! /usr/bin/perl
###################################################################################
#              Dan Cardamore <wombat@hld.ca>
#                   Copyright 2000 all rights reserved
#                   This software is released under the GNU GPL license
###################################################################################
# 	$rcs = ' $Id: index.cgi,v 1.4 2001/12/04 22:07:42 dan Exp $ ' ;	
###################################################################################
use strict;
use CGI qw(param);
use POSIX ":sys_wait_h";
use File::stat;
use Date::Manip;
use vars qw/$dbname $dbhost $dbuser $dbpass $icon_url $header $footer $background $site_logo $site_url/;

###################################################################################
##################   User Configuration Data          #############################
###################################################################################
# this is the url of the directory where you have your icons
$icon_url = 'http://hld.ca/icons';
$site_logo = 'http://hld.ca/images/hld.gif';
$site_url = 'http://www.hld.ca';
# this is the path to header.shtml
$header = '/home/httpd/html/template/header.shtml';
# this is the path to footer.shtml
$footer = '/home/httpd/html/template/footer.shtml';
# this is the background color for the top row of the table
$background = '#bebebe';

##################################################################################
###############  END OF CONFIGURATION DATA        ################################
##################################################################################

sub redirect {
  my $file = param('file');

  my $pwd = `pwd`;
  chomp $pwd;
  my $dbfile = relpath("$pwd" ."/$file");


  my ($hits) = 0;

  print "Location: $file\n\n";
}

sub handleThisDir {
  my $pwd = `pwd`;
  my ($name, $date, $size, $random, $thumbed);
  chomp $pwd;

  &printDirs($pwd);
  &printFiles($pwd);
  return;
}

sub printDirs {
  my ($pwd) = @_;
  # start by printing the table header
  print "<font size=\"+1\">\n";
  print "<table width=\"100%\" border=\"0\" cellspacing=\"3\" cellpadding=\"4\" valign=\"top\">\n";
  print "<tr valign=\"bottom\">\n";
  print "<td bgcolor=$background><b>Name</b></td>\n";
  print "<td bgcolor=$background><b>Size</b></td>\n";
  print "<td bgcolor=$background><b>Type</b></td>\n";
  print "</tr>\n\n";

  my @allfiles = get_files();
  foreach my $temp_file (@allfiles)	{
	if ($temp_file eq ".") { next; }
	my $dbfile = relpath("$pwd" ."/$temp_file");

	if (-d $temp_file) {           #If it is a directory
	  print "<tr valign=\"bottom\">\n";
	  my $link = "index.cgi?file=$temp_file";
	  if (-e "$dbfile/index.cgi")	{
		$link = "$temp_file";
	  }
	  if ($temp_file eq '..') {
		print "<td><img src=\"$icon_url/folder.gif\"> \n";
		print "<font size=\"-1\"><a href=\"$link\">".
		  "<b>$temp_file</b></a></font></td>\n";
		print "<td><font size=\"-1\">N/A</font></td>\n";
		print "<td><font size=\"-1\">Directory</font></td>\n";
	  }
	  else	{
		print "<td><img src=\"$icon_url/folder.gif\"> \n";
		print "<font size=\"-1\"><a href=\"$link\">" .
		  "<b>$temp_file</b></a></font></td>\n";
		print "<td><font size=\"-1\">N/A</font></td>\n";
		print "<td><font size=\"-1\">Directory</font></td>\n";
	  }
	  print "</tr>\n\n";
	}
  }
}

sub printFiles {
  my ($pwd) = @_;

  my @allfiles = get_files();
  foreach my $temp_file (@allfiles)	{
	if ($temp_file eq ".") { next; }
	my $dbfile = relpath("$pwd" ."/$temp_file");

	if (-f $temp_file and ($temp_file ne "index.cgi") and ($temp_file ne ".welcome.html") and
		($temp_file ne ".htaccess"))  {
	  my @fnameExt = split(/\./,$temp_file);			
	  my $ext = $fnameExt[$#fnameExt];

	  my $icon = "generic.gif";
	  if ($ext =~ /htm/i || $ext =~ /html/i) { $icon = "portal.gif"; }
	  if ($ext =~ /txt/i) { $icon = "a.gif"; }
	  if ($ext =~ /pl/i || $ext =~ /cgi/i) { $icon = "script.gif"; }
	  if ($ext =~ /mov/i || $ext =~ /mpg/i) { $icon = "small/movie.gif"; }
	  if ($ext =~ /zip/i || $ext =~ /gz/i) { $icon = "compressed.gif"; }
	  if ($ext =~ /gif/i) { $icon = "image2.gif"; }
	  if ($ext =~ /pdf/i) { $icon = "pdf.gif"; }
	  if ($ext =~ /jpg/i || $ext =~ /jpeg/i) { $icon = "image2.gif"; }

	  print "<tr valign=\"bottom\">\n";

	  my $sref = stat($temp_file);
	  my $size = $sref->size / 1024;
          my $old_temp_file = $temp_file;
	  $temp_file =~ s/ /%20/g;

	  print "<td><img src=\"$icon_url/$icon\"> <font size=\"-1\">" .
		"<a href=\"index.cgi?file=$temp_file\"><b>$old_temp_file</b></a></font></td>\n";
	  print "<td><font size=\"-1\">$size kB</font></td>\n";
	  print "<td><font size=\"-1\">$ext</font></td>\n";
	  print "</tr>\n\n";
	}
  }
  print "</table><br><br>\n";
  return;
}


sub get_files {
  opendir (DIR, '.');
  my @allfiles = readdir(DIR);
  closedir (DIR);

  @allfiles = sort @allfiles;
  return @allfiles;
}

sub print_header {
  print "Content-type: text/html\n\n";
  open (FILE, "<$header");
  flock (FILE, 2);
  my @header = <FILE>;
  flock (FILE, 8);
  close (FILE);
  print @header;
  print "\n\n";
  print "<p align=\"right\"><a href=$site_url><img src=$site_logo border=0></a></p>\n\n";
}

sub print_footer {
  open (FILE, "<$footer");
  flock (FILE, 2);
  my @footer = <FILE>;
  flock (FILE, 8);
  close (FILE);
  print @footer;
}

sub print_welcome {
  if (-e ".welcome.html"){
	print `cat .welcome.html`;
  }
}


sub relpath($) {
  my $file = shift;
  my $newfile = "";
  $file =~ s/\n//g;  # remove new lines
  my @peices = split /\//, $file;

  for (my $i = 0; $i <= $#peices; $i++)	{
	if ($peices[$i + 1] eq "..") {
	  last;
	}
	if ($peices[$i] ne ".")	  {
	  $newfile .= "/$peices[$i]";
	}
  }
  $newfile =~ s/\/\//\//g;
  return $newfile;
}




#  displays on pic and has next, prev, and back buttons
sub displayPic() {
  my $picNum = param('picNum');
  open (FILE, "<photo.dat") or die print "Error opening photo.dat";
  flock (FILE, 2);
  my @file = <FILE>;
  flock (FILE, 8);
  close (FILE);

  chomp @file;

  my ($albumName, $albumDesc) = split /~:~/, $file[0];
  my ($bgcolor, $fontcolor) = ($file[2], $file[3]);
  my ($picName, $picDesc) = split /~:~/, $file[$picNum + 4];

  my $prev = $picNum - 1;
  my $next = $picNum + 1;

  print "<html><head><title>Album: $albumName  Picture: $picName</title>";
  print "</head><body bgcolor=$bgcolor>\n";
  print "<center>\n";
  print "<a href=palbum.pl?option=displayPic\&picNum=$prev>Previous</a>  ";
  print "<a href=palbum.pl>Index</a>  ";
  print "<a href=palbum.pl?option=displayPic\&picNum=$next>Next</a><br><br>";

  print "<img src=$picName border=0 alt=$picName><br>\n";
  print "<font color=$fontcolor>$picDesc</font><br><br>";

  print "<a href=palbum.pl?option=displayPic\&picNum=$prev>Previous</a>  ";
  print "<a href=palbum.pl>Index</a>  ";
  print "<a href=palbum.pl?option=displayPic\&picNum=$next>Next</a><br><br>";
  print "</center></body></html>\n";
}

sub generateIndex() {
  if ( -e "photo.dat" ) { die print "Error: photo.dat exists"; }

  opendir (DIR, ".");
  my @allpics = readdir(DIR);
  closedir(DIR);

  chomp @allpics;
  @allpics = sort @allpics;

  my @pics;
  foreach my $pic (@allpics)	{
	unless ( -f "$pic") { next; }  # only look at files
	if ( $pic eq "photo.dat" ) { next; }  # ignore photo.dat
	if ( $pic eq "index.cgi" ) { next; }  # ignore photo.dat
	if ( $pic eq "palbum.pl" ) { next; }  # ignore photo.dat
	if ( $pic =~ /PAsmall/ ) { next; }  # ignore thumbnails.

	push @pics, $pic;
  }

  my $albumName = param('albumName');
  my $albumDesc = param('albumDesc');

  my $bgcolor = param('bgcolor');
  my $fontcolor = param('fontcolor');
  my $picNum = param('picNum');

  $picNum = 10 unless (defined $picNum);
  $bgcolor = "white" unless (defined $bgcolor);
  $fontcolor = "blue" unless (defined $fontcolor);

  my $date = ParseDate("today");

  open (FILE, ">photo.dat") or die print "Cannot open photo.dat for writing";
  flock (FILE, 2);

  print FILE "$albumName~:~$albumDesc~:~$date\n";
  print FILE "$picNum\n$bgcolor\n$fontcolor\n";

  foreach my $pic (@pics)	{
	my $picDesc = param($pic);
	if (not defined $picDesc or $picDesc eq "")	  {
	  $picDesc = "No Description";
	}
	print FILE "$pic~:~$picDesc\n";
  }

  flock (FILE, 8);
  close (FILE);
}

sub generateIndexForm() {
  if ( -e "photo.dat" ) { die print "Error: photo.dat exists"; }

  opendir (DIR, ".");
  my @allpics = readdir(DIR);
  closedir(DIR);

  chomp @allpics;
  @allpics = sort @allpics;

  my @pics;
  foreach my $pic (@allpics)	{
	unless ( -f "$pic") { next; }  # only look at files
	if ( $pic eq "photo.dat" ) { next; }  # ignore photo.dat
	if ( $pic eq "index.cgi" ) { next; }  # ignore photo.dat
	if ( $pic eq "palbum.pl" ) { next; }  # ignore photo.dat
	if ( $pic =~ /PAsmall/ ) { next; }  # ignore thumbnails.

	`convert -geometry 80x80 $pic PAsmall$pic`;
	push @pics, $pic;
  }

  print "<html><head><title>Generate Album</title></head>";
  print "<body bgcolor=white><center>\n";
  print "<font color=blue><b>Note:  The thumbnails have already been created.";
  print "  You now need to customize your photo album</b></font><br>\n";

  print "<form action=palbum.pl method=post>";
  print "<input type=hidden name=option value=generateIndex>";

  # Global album properties
  print "<table width=100% border=1 cellpadding=0>\n";
  print "<tr><td colspan=2 align=center>Album Properties</td></tr>\n";
  print "<tr><td>Album Name</td><td><input type=text name=albumName></td></tr>\n";
  print "<tr><td>Album Description</td><td><input type=text " .
	"name=albumDesc></td></tr>\n";
  print "<tr><td>Background Color</td><td><input type=text name=bgcolor></td></tr>";
  print "<tr><td>Font Color</td><td><input type=text name=fontcolor></td></tr>";
  print "<tr><td>Pics per page</td><td><input type=text name=picNum></td></tr>";
  print "</table>";

  print "<hr>\n";

  # each picture properties
  print "<table border=1 width=100% cellspacing=0>\n";
  print "<tr><td><b>Thumbnail</b></td><td>Description</td></tr>\n";
  foreach my $pic (@pics)	{
	print "<tr><td><img src=PAsmall$pic alt=$pic><br>$pic</td>";
	print "<td><input type=text name=\"$pic\"></td></tr>\n";
  }

  print "</table>\n";
  print "<input type=submit value=OK>\n";
  print "</form>\n";
  print "</center></body></html>\n";
}



if (defined param('file')) {
  &redirect;
}
else {
  my $pwd = `pwd`;
  chomp $pwd;
  my $dbfile = relpath("$pwd");

  &print_header;
  &print_welcome;
  &handleThisDir;
  &print_footer;
}

