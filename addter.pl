#!/usr/bin/perl
open(INPUT,"$ARGV[0]");
open(OUTPUT,">$ARGV[1]");
@molecule=<INPUT>;
$k=substr($molecule[0],22,4);
$res=0;
$atom=0;
for($i=0;$i<@molecule;$i++)
{$res_num=substr($molecule[$i],22,4);
if($k==$res_num)
{$residue[$res][$atom]=$molecule[$i];
$atom++;}
if($k!=$res_num)
{$res++;
$atom=0;
$residue[$res][$atom]=$molecule[$i];
$atom++;}
$k=$res_num;}
for($i=0;$i<=$res;$i++)
{$link=0;
foreach $line (@{$residue[$i]})
{if(substr($line,12,3) eq " C ")
{foreach $line2 (@{$residue[$i+1]})
{if(substr($line2,12,3) eq " N ")
{$x1=substr($line,30,8);
$y1=substr($line,38,8);
$z1=substr($line,46,8);
$x2=substr($line2,30,8);
$y2=substr($line2,38,8);
$z2=substr($line2,46,8);
$dist=sqrt(($x1-$x2)**2+($y1-$y2)**2+($z1-$z2)**2);
if($dist<1.5)
{$link=1;}}}}
print OUTPUT ($line);}
if($link==0)
{print OUTPUT ("TER\n");}}
