#!/usr/bin/python

class gmxtop:
    # private variables
    _atomtype = list()
    _charge = dict()
    _resitype = list()
    _resi = dict()
    _resi_amber = dict()
    _vdw = dict()

    def __init__(self,nonbondfile,rtpfile,waterfile):
        self.make_amb2gmx_table()

        for line in open(nonbondfile):
            if line.strip()[0] not in (';','['):
                items = line.split()
                t = items[0]
                sigma = float(items[5])
                epsion = float(items[6])
                self._atomtype.append(t)
                self._vdw[t] = sigma,epsion 

        for name,resilines in self._nextresiline(rtpfile):
            self._resitype.append(name)
            self._resi[name] = list()
            self._resi_amber[name] = list()
            for line in resilines:
                items = line.split()
                n = items[0]

                ### For Amber name
                try:
                    na = self.get_amb2gmx_name(name,n) 
                except:
                    na = n

                t = items[1]
                c = float(items[2])
                s,e = self._vdw[t]
                self._resi[name].append( (n,s,e,c) )
                
                ### For Amber name
                self._resi_amber[name].append( (na,s,e,c) )
        
        for name,resilines in self._nextresiline(waterfile):
            name = 'HOH'
            self._resitype.append(name)
            self._resi[name] = list()
            for line in resilines:
                items = line.split()
                n = items[4]
                t = items[1]
                c = float(items[6])
                s,e = self._vdw[t]
                self._resi[name].append( (n,s,e,c) )

    def _nextresiline(self,rtpfile):
        lines = list()
        name = None
        atomflag = False
        for line in open(rtpfile):
            if not line.strip():
                continue
            elif line.strip()[0] in ('#',';'):
                continue
            elif '[' in line and ']' in line:
                mid = line.split()[1]
                if len(mid) <= 4:
                    if len(lines) != 0:
                        yield name,lines
                        name = mid
                        lines = list()
                else:
                    pass
                if mid == 'atoms' :
                    atomflag = True
                else:
                    atomflag = False
            else:
                if atomflag :
                    if line.strip() != '' :
                        lines.append(line)
                else:
                    pass
        yield name,lines

    def get_resilist(self):
        return self._resitype

    def get_resi( self, name ):
        return self._resi[name]
                        
    def debug(self):
        print "ATOM TYPE"
        print self._atomtype
        print "RESI TYPE"
        print self._resitype
        for t in self._resitype:
            print t
            print self._resi[t]

    def make_amb2gmx_table(self):
        self.amb2gmx_table =  dict()
        self.wildcard_types = dict()
        for line in self.amb2gmx_table_str.split('|'):
            resi,namea,nameg = line.split(':')
            resi = resi.strip()
            if resi != "*":
                namea = namea.strip()
                nameb = nameb.strip()
                if self.amb2gmx_table.has_key(resi):
                    self.amb2gmx_table[resi][namea]=nameb
                else:
                    self.amb2gmx_table[resi] = dict()
                    self.amb2gmx_table[resi][namea]=nameb
            else:
                self.wildcard_types[namea] = nameb
        pass

    def get_amb2gmx_name(self, resi,n ):
        if self.wildcard_types.has_key(n):
            return self.wildcard_types[n]
        else:
            try:
                return self.wildcard_types[resi][n]
            except:
                return n

    amb2gmx_table_str = '''
        WAT: OW :   O| 
        WAT:1HW :  H1|
        WAT:2HW :  H2|
        ILE:1HG2:HG21|
        ILE:2HG2:HG22|
        ILE:3HG2:HG23|
        ILE:1HG1:HG12|
        ILE:2HG1:HG13|
        ILE: HD1:HD11|
        ILE: HD2:HD12|
        ILE: HD3:HD13|
        ILE: CD : CD1|
        VAL:1HG1:HG11|
        VAL:2HG1:HG12|
        VAL:3HG1:HG13|
        VAL:1HG2:HG21|
        VAL:2HG2:HG22|
        VAL:3HG2:HG23|
        GLY: HA1: HA2|
        GLY: HA2: HA3|
        TYR: HB1: HB2|
        TYR: HB2: HB3|
        THR:1HG2:HG21|
        THR:2HG2:HG22|
        THR:3HG2:HG23|
        CYS: HB1: HB2|
        CYS: HB2: HB3|
        CYX: HB1: HB2|
        CYX: HB2: HB3|
        ASN: HB1: HB2|
        ASN: HB2: HB3|
        ASN:1HD2:HD21|
        ASN:2HD2:HD22|
        PRO: HD1: HD2|
        PRO: HD2: HD3|
        PRO: HG1: HG2|
        PRO: HG2: HG3|
        PRO: HB1: HB2|
        PRO: HB2: HB3|
        GLN: HB1: HB2|
        GLN: HB2: HB3|
        GLN: HG1: HG2|
        GLN: HG2: HG3|
        GLN:1HE2:HE21|
        GLN:2HE2:HE22|
        SER: HB1: HB2|
        SER: HB2: HB3|
        LEU: HB1: HB2|
        LEU: HB2: HB3|
        LEU:1HD1:HD11|
        LEU:2HD1:HD12|
        LEU:3HD1:HD13|
        LEU:1HD2:HD21|
        LEU:2HD2:HD22|
        LEU:3HD2:HD23|
        MET: HB1: HB2|
        MET: HB2: HB3|
        MET: HG2: HG3|
        MET: HG1: HG2|
        PHE: HB1: HB2|
        PHE: HB2: HB3|
        TRP: HB1: HB2|
        TRP: HB2: HB3|
        ASP: HB1: HB2|
        ASP: HB2: HB3|
        GLU: HB1: HB2|
        GLU: HB2: HB3|
        GLU: HG1: HG2|
        GLU: HG2: HG3|
        HIP: HB1: HB2|
        HIP: HB2: HB3|
        HIS: HB1: HB2|
        HIS: HB2: HB3|
        HID: HB1: HB2|
        HID: HB2: HB3|
        HIE: HB1: HB2|
        HIE: HB2: HB3|
        LYS: HB1: HB2|
        LYS: HB2: HB3|
        LYS: HG1: HG2|
        LYS: HG2: HG3|
        LYS: HD1: HD2|
        LYS: HD2: HD3|
        LYS: HE1: HE2|
        LYS: HE2: HE3|
        ARG: HB1: HB2|
        ARG: HB2: HB3|
        ARG: HG1: HG2|
        ARG: HG2: HG3|
        ARG: HD1: HD2|
        ARG: HD2: HD3|
        ARG:1HH1:HH11|
        ARG:2HH1:HH12|
        ARG:1HH2:HH21|
        ARG:2HH2:HH22|
        HOH: OW :   O|
        HOH: HW1:  H1|
        HOH:1HW :  H1|
        HOH: HW2:  H2|
        HOH:2HW :  H2|
        # *: OC1: O  |
        # *: OC2: OXT|
        # *:  H1: H1 |
        # *:  H2: H2 |
        # *:  H3: H3 |
    '''
