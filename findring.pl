#!/usr/bin/perl
use warnings;

# name: findring.pl
# Scrip which determines all possible cycles in mol2 file<s>.
# Written by Yu Zhou, Huang lab in NIBS, 2009-12-21; modified on 2010-01-10.
#
# This is only a part of the whole ring perception program, which was simplified to present in perl courses.
#
# Usage: findring.pl file1.mol2 <file2.mol2 file3.mol2 ...>
#
# Ring detection algorithm taken from:
# Th. Hanser, Ph. Jauffret, G. Kaufmann   J. Chem. Inf. Comput. Sci.   1996, vol36, p. 1146-1152
#
# Appreciation to Zhiya Sheng for tips and Dr.Huang for guidance.
#
# Copyright (C)  2010  NIBS

### check the parameter
if (@ARGV < 1)
{
    die "Usage: $0 mol2file(s)\n";
}

### load the mol2 file
foreach $file (@ARGV)
{
    next unless ($file =~ /mol2/i);
    $file =~ s/\..*?$//; # remove file extension
    open (MOL2FILE, "$file.mol2") or die "Can not open file $file.mol2!\n";

    print ">>>>> processing $file.mol2...\n";

    my %type = ();
    my %spectype = ();
    my @m_bond = ();
    my @ring = ();
    my @ringbond = ();

### data recording
    {
        local $/ = "@<TRIPOS>";
        while (<MOL2FILE>)
        {
            @data = split /\n+/;
            if ($data[0] eq "ATOM")
            {
                shift @data;
                pop @data;
                foreach (@data)
                {
                    @tmp = split;
                    $type{$tmp[0]} = $tmp[5];
                }
            }
            elsif ($data[0] eq "BOND")
            {
                shift @data;
                pop @data;
                foreach (@data)
                {
                    @tmp = split;
                    push @m_bond, [ @tmp ];
                }
            }
        }
    }
# uncomment to debug: print out the 
#    foreach $i (keys %type)
#    {
#        print "type $i: $type{$i}\n";
#    }
#
#    foreach $i (0 .. $#m_bond)
#    {
#        print "m_bond $i: $m_bond[$i]->[0] $m_bond[$i]->[1] $m_bond[$i]->[2]\n";
#    }

### initialize edge
    my %edge = ();
    foreach $i (0 .. $#m_bond)
    {
        $edge{$i}->[0] = $m_bond[$i]->[1];
        $edge{$i}->[1] = $m_bond[$i]->[2];
    }
# uncomment to debug: print out the %edge
#   foreach $i (0 .. $#m_bond)
#   {
#       print "edge $i: ==> @{$edge{$i}} \n";
#   }

### initialize neighbors
    my %neighbor = ();
    foreach $i (keys %type)
    {
        for $j (0 .. $#m_bond)
        {
            $a1 = $m_bond[$j]->[1];
            $a2 = $m_bond[$j]->[2];
            if ($a1 == $i)
            {
                $atom = $a2;
                push @{$neighbor{$i}}, $atom;
            }
            if ($a2 == $i)
            {
                $atom = $a1;
                push @{$neighbor{$i}}, $atom;
            }
        }
    }

### initialize vertices (key: atom number; value: connectivity--number of neighbors)
    my %vertex = ();
    foreach $i (keys %type)
    {
        $nn = @{$neighbor{$i}};
        $vertex{$i} = $nn;
    }

### remove appendage vertices (terminal edges)
    $oneneighbor = 1;
    while ($oneneighbor > 0)
    {
        foreach $i (keys %vertex)
        {
            if ($vertex{$i} == 1)
            {
                delete $vertex{$i};
                foreach $j (keys %edge)
                {
                    $k1 = $edge{$j}->[0];
                    $k2 = $edge{$j}->[1];
                    if ($k1 == $i)
                    {
                        delete $edge{$j};
                        $vertex{$k2} --;
                    }
                    if ($k2 == $i)
                    {
                        delete $edge{$j};
                        $vertex{$k1} --;
                    }
                }
            }
        }
        $oneneighbor = 0;
        foreach $i (keys %vertex)
        {   
            $oneneighbor ++ if $vertex{$i} == 1;
        }
    }

### reduce the graph further by collapsing other vertices
    while (scalar (keys %vertex) > 0)
    {
        foreach $i (sort {$vertex{$a} <=> $vertex{$b}} keys %vertex)
        {
            $curvert = $i; # sort the vertex hash by increasing number of neighbors and pick the lowest one
            last;
        }
### pick all the pairs containing picked vertex
        my %specedge = ();
        foreach $i (keys %edge)
        {
            my @thisedge = @{$edge{$i}};
            $firstel = $thisedge[0];
            $lastel = $thisedge[$#thisedge];
    
            if ($firstel == $curvert and $lastel != $curvert)
            {
                $specedge{$i}[0] = 'F';
                push @{$specedge{$i}}, @thisedge;
            }
            if ($firstel != $curvert and $lastel == $curvert)
            {
                $specedge{$i}[0] = 'L';
                push @{$specedge{$i}}, @thisedge;
            }
            if ($firstel == $curvert and $lastel == $curvert)
            {
                $specedge{$i}[0] = 'B';
                push @{$specedge{$i}}, @thisedge;
            }
        }
# uncomment to debug: print out %specedge
#    foreach $i (keys %specedge)
#    {
#        print "specedge: $i -----> @{$specedge{$i}} \n";
#    }

### pick a number for a label
        $maxlabel = -1;
        foreach $i (keys %edge)
        {
            $maxlabel = $i if $i > $maxlabel;
        }

### join the two edges pairwise
        my @newedge = ();
EDGE1:  foreach $i (keys %specedge)
        {
            my @edge1 = @{$specedge{$i}};
            next EDGE1 if $edge1[0] =~ 'B';
EDGE2:      foreach $j (keys %specedge)
            {
                my @edge2 = @{$specedge{$j}};
                next EDGE2 if $edge2[0] =~ 'B';
                unless ($i >= $j)
                {
                    @tmp1 = @edge1;
                    shift @tmp1;
                    @tmp2 = @edge2;
                    shift @tmp2;
                    if ($edge1[0] =~ 'F')
                    {
                        @tmp1 = reverse @tmp1;
                    }
                    if ($edge2[0] =~ 'L')
                    {
                        @tmp2 = reverse @tmp2;
                    }
                    shift @tmp2;
                    push (@tmp1, @tmp2);
                    push @newedge, [ @tmp1 ];
                }
            }
        }
        foreach $i (0 .. $#newedge)
        {
            $maxlabel ++;
            for $j (0 .. $#{$newedge[$i]})
            {
                push @{$edge{$maxlabel}}, $newedge[$i][$j];
            }
        }
CLEAN:  foreach $i (keys %edge)
        {
            my @thisedge = @{$edge{$i}};
            $firstel = $thisedge[0];
            $lastel = $thisedge[$#thisedge];
            if ($firstel == $lastel)
            {
                $n = $#thisedge - 1;
            }
            else
            {
                $n = $#thisedge;
            }

            for $j (0 .. $n)
            {
                for $k (0 .. $j-1)
                {
                    if ($thisedge[$k] == $thisedge[$j])
                    {
                        delete $edge{$i};
                        next CLEAN;
                    }
                }
            }
            if ($firstel == $curvert or $lastel == $curvert)
            {
                if ($firstel == $lastel)
                {
                    push @ring, [ @thisedge ];
                }
                delete $edge{$i};
                next CLEAN;
            }
        }
# uncomment to debug
# foreach $i (keys %edge)
# {
#     print "NEW EDGES: $i ----> @{$edge{$i}}\n";
# }
        delete $vertex{$curvert};

### recalculate connectivities
        foreach $i (keys %vertex)
        {
            $vertex{$i} = 0; # zero out connectivities first
        }
        foreach $i (keys %vertex) # to improve
        {
            foreach $j (keys %edge)
            {
                my @thisedge = @{$edge{$j}};
                $firstel = $thisedge[0];
                $lastel = $thisedge[$#thisedge];
                $vertex{$i}++ if ($firstel == $i or $lastel == $i);
            }
        }
    } # end while (scalar (keys %vertex) > 0)

### print out the ring information and record ring bonds
    foreach $i (0 .. $#ring)
    {
        print "RING: $i ===> @{$ring[$i]}\n";
        foreach $j (0.. $#{$ring[$i]}-1)
        {
            $tmp[0] = $ring[$i][$j];
            $tmp[1] = $ring[$i][$j+1];
            push @ringbond, [ @tmp ];
        }
    }
# to print all ring bonds
#    foreach $i (0 .. $#ringbond)
#    {
#        print "RING BONDS: $i ---> $ringbond[$i][0] $ringbond[$i][1]\n";
#    }

    print ">>>>> calculation for $file.mol2 is over!\n";
}
