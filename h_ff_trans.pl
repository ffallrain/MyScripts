#!/usr/bin/perl
#h_ff_trans.pl
#translating hydrogen atom names amoung force field
#Version I
#NOV. 18th, 2010
#S. Peng
#
#take care of HIS in PDB,  HSD in CHARMM, NMA in OPLS and CT3 in CHARMM
#CYM and CYX in CHARMM, CYM in OPLS, ASZ and GLZ in AMBER, CHARMM, OPLS

########################################################################

$matrix=$ARGV[0];
$matrix="/home/fuqiuyu/.ffallrain/h_atm_matrix";
$in=$ARGV[1];
chomp($in);
$out=$in.'.out';
$err=$in.'.err';
#echo "type of the input file:(PDB,DOCK,AMBER,CHARMM,OPLS)"
$intype=$ARGV[2];
chomp($intype);
#echo "type of the output file:(PDB,DOCK,AMBER,CHARMM,OPLS)"
$outtype=$ARGV[3];
chomp($outtype);
#echo "translating the $(intype) atom type to $(outtype)"

########################################################################

$inlabel=0;
$outlabel=0;
%inout=();

########################################################################

if($intype eq "PDB" ){$inlabel=1;}
elsif($intype eq "DOCK"   ){$inlabel=2;}
elsif($intype eq "AMBER"  ){$inlabel=3;}
elsif($intype eq "CHARMM" ){$inlabel=4;}
elsif($intype eq "OPLS"  ){$inlabel=5;}
else{print "The input format is not supported!";}

if($outtype eq "PDB" ){$outlabel=1;}
elsif($outtype eq "DOCK"   ){$outlabel=2;}
elsif($outtype eq "AMBER"  ){$outlabel=3;}
elsif($outtype eq "CHARMM" ){$outlabel=4;}
elsif($outtype eq "OPLS"  ){$outlabel=5;}
else{print "The output format is not supported!";}

########################################################################

open(NAME,"< $matrix");
while($line=<NAME>){
      if(substr($line,0,1)ne'#'){
         @list=split(/;/,$line);
         $inout{$list[0].$list[$inlabel]}=$list[$outlabel];
      }
}
close(NAME);

########################################################################

open(IN,"< $in");
open(OUT,"> $out");
open(ERR,"> $err");
while($line=<IN>){
     if(substr($line,0,6)eq'ATOM  '){
       if(defined($inout{substr($line,17,3).substr($line,12,4)})){
          substr($line,12,4,$inout{substr($line,17,3).substr($line,12,4)});
       }
       else{
          print ERR substr($line,17,3).';'.substr($line,12,4).';'."\n";
       }
     }
     print OUT $line;
}
close(IN);
close(OUT);
close(ERR);

########################################################################

`grep -v NNNN $out > ztmp`;
`mv ztmp $out`;

########################################################################
