#!/usr/bin/perl
###################################################################################
#              Dan Cardamore <wombat@hld.ca>
#                   Copyright 2000 all rights reserved
#                   This software is released under the GNU GPL license
###################################################################################
# 	$rcs = ' $Id: index.cgi,v 1.1 2001/01/24 03:36:30 wombat Exp $ ' ;	
###################################################################################
use strict;
use CGI qw(param);
use DBI;
use POSIX ":sys_wait_h";
use File::stat;
use vars qw/$dbname $dbhost $dbuser $dbpass $icon_url $header $footer $background $site_logo $site_url/;

###################################################################################
##################   User Configuration Data          #############################
###################################################################################
# these are for connecting to the Postgres database
$dbname = 'wwwindex';
$dbhost = 'localhost';
$dbuser = 'wwwindex';
$dbpass = '';

# this is the url of the directory where you have your icons
$icon_url = 'http://base.hld.ca/cgi/index_gifs';
$site_logo = 'http://base.hld.ca/images/hld.gif';
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

sub redirect
{
		my $file = param('file');
		my $dbh = DBI->connect("dbi:Pg:dbname=$dbname;host=$dbhost", "$dbuser", "$dbpass") or die $!;
		my $pwd = `pwd`;
		chomp $pwd;
		my $dbfile = relpath("$pwd" ."/$file");		
				
		my $sth = $dbh->prepare( "SELECT hits FROM files where name='$dbfile'" );
		$sth->execute;
		my ($hits) = $sth->fetchrow_array;
		$hits++;
		$sth = $dbh->prepare( "UPDATE files set hits='$hits' where name='$dbfile'" );
		$sth->execute;
		$dbh->disconnect;

		print "Location: $file\n\n";
}

sub print_files {
		my $dbh = DBI->connect("dbi:Pg:dbname=$dbname;host=$dbhost", "$dbuser", "$dbpass") or die $!;
		my $pwd = `pwd`;

		# start by printing the table header

		print "<font size=\"+1\">\n";
		print "<table width=\"100%\" border=\"0\" cellspacing=\"3\" cellpadding=\"4\" valign=\"top\">\n";
		print "<tr valign=\"bottom\">\n";
		print "<td bgcolor=$background><b>Name</b></td>\n";
		print "<td bgcolor=$background><b>Size</b></td>\n";
		print "<td bgcolor=$background><b>Hits</b></td>\n";
		print "<td bgcolor=$background><b>Type</b></td>\n";
		print "<td bgcolor=$background><b>Description</b></td>\n";
		print "</tr>\n\n";

		my @allfiles = get_files();
		foreach my $temp_file (@allfiles)
		{
				if ($temp_file eq ".") { next; }
				chomp $pwd;
				my $dbfile = relpath("$pwd" ."/$temp_file");
				
				my $sth = $dbh->prepare( "SELECT * FROM files where name='$dbfile'" );
				$sth->execute;
				my ($fname, $hits, $description) = $sth->fetchrow_array;
				if (not defined $hits)
				{
						$sth = $dbh->prepare( "INSERT into files values('$dbfile', '0', '')" );
						$sth->execute;
						$hits = 0;
				}
				
				if (-d $temp_file)            #If it is a directory
				{
						print "<tr valign=\"bottom\">\n";
						my $link = "index.cgi?file=$temp_file";
						if (-e "$dbfile/index.cgi")
						{
								$link = "$temp_file";
						}
						if ($temp_file eq '..')
						{
								print "<td><img src=\"$icon_url/folder.gif\"> \n";
								print "<font size=\"-1\"><a href=\"$link\">".
										"<b>$temp_file</b></a></font></td>\n";
								print "<td><font size=\"-1\">N/A</font></td>\n";
								print "<td><font size=\"-1\">$hits</font></td>\n";
								print "<td><font size=\"-1\">Directory</font></td>\n";								
								print "<td><font size=\"-1\">Go Up One Directory</font></td>\n";
						}
						else
						{
								if (not defined $description)
								{
										$description = "";
								}
								
								print "<td><img src=\"$icon_url/folder.gif\"> \n";
								print "<font size=\"-1\"><a href=\"$link\">" .
										"<b>$temp_file</b></a></font></td>\n";
								print "<td><font size=\"-1\">N/A</font></td>\n";
								print "<td><font size=\"-1\">$hits</font></td>\n";
								print "<td><font size=\"-1\">Directory</font></td>\n";
								print "<td><font size=\"-1\">$description</font></td>\n";
						}
						print "</tr>\n\n";
				}		
				
				if (-f $temp_file and ($temp_file ne "index.cgi") and ($temp_file ne ".welcome.html") and
						($temp_file ne ".htaccess"))
				{
						my @fnameExt = split(/\./,$temp_file);			
						my $ext = $fnameExt[$#fnameExt];
						
						if (not defined $description)
						{
								$description = "";
						}
						
						my $icon = "file.gif";
						if ($ext =~ /htm/i || $ext =~ /html/i) { $icon = "html.gif"; }
						if ($ext =~ /txt/i) { $icon = "txt.gif"; }
						if ($ext =~ /pl/i || $ext =~ /cgi/i) { $icon = "cgi.gif"; }
						if ($ext =~ /zip/i || $ext =~ /gz/i) { $icon = "zip.gif"; }
						if ($ext =~ /exe/i) { $icon = "exe.gif"; }
						if ($ext =~ /gif/i) { $icon = "gif.gif"; }
						if ($ext =~ /jpg/i || $ext =~ /jpeg/i) { $icon = "jpg.gif"; }
		
						print "<tr valign=\"bottom\">\n";
						
						my $sref = stat($temp_file);
						my $size = $sref->size / 1024;
						$temp_file =~ s/ /%20/g;
						print "<td><img src=\"$icon_url/$icon\"> <font size=\"-1\">" .
								"<a href=\"index.cgi?file=$temp_file\"><b>$temp_file</b></a></font></td>\n";
						print "<td><font size=\"-1\">$size kB</font></td>\n";
						print "<td><font size=\"-1\">$hits</font></td>\n";
						print "<td><font size=\"-1\">$ext</font></td>\n";
						print "<td><font size=\"-1\">$description</font></td>\n";
						print "</tr>\n\n";
				}
		}
		print "</table><br><br>\n";
		$dbh->disconnect;
}

################
# sub routines #
################

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


if (defined param('file'))
{
		&redirect;
}
else
{
		my $dbh = DBI->connect("dbi:Pg:dbname=$dbname;host=$dbhost", "$dbuser", "$dbpass") or die $!;
		my $pwd = `pwd`;
		chomp $pwd;
		my $dbfile = relpath("$pwd");		
		
		my $sth = $dbh->prepare( "SELECT hits FROM files where name='$dbfile'" );
		$sth->execute;
		my ($hits) = $sth->fetchrow_array;
		$hits++;
		$sth = $dbh->prepare( "UPDATE files set hits='$hits' where name='$dbfile'" );
		$sth->execute;
		$dbh->disconnect;

		&print_header;
		&print_welcome;
		&print_files;
		&print_footer;
}

