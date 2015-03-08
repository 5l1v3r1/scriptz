#!/usr/bin/perl
#Description: get a list of your contributions on github.com
#Source: https://stackoverflow.com/questions/21322778/how-do-i-get-a-list-of-all-the-github-projects-ive-contributed-to-in-the-last-y
#License: CC-BY-SA 3.0 (http://creativecommons.org/licenses/by-sa/3.0/)
#Copyright: (c) 2014 theory (https://stackoverflow.com/users/79202/theory)
use v5.12;
use warnings;
use utf8;
my $uname = 'nodiscc';

my %projects;
for my $year (2011..2014) {
    for my $month (1..12) {
        last if $year == 2014 && $month > 1;
        my $from = sprintf '%4d-%02d-01', $year, $month;
        my $to   = sprintf '%4d-%02d-01', $month == 12 ? ($year + 1, 1) : ($year, $month + 1);
        my $res = `curl 'https://github.com/$uname?tab=contributions&from=$from&to=$to' | grep 'class="title"'`;
        while ($res =~ /href="([^"?]+)/g) {
            my (undef, $user, $repo) = split m{/} => $1;
            $projects{"$user/$repo"}++;
        }
    }
}

say "$projects{$_}: $_" for sort keys %projects;