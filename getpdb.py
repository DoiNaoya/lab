import time, subprocess, random, string, os
from sys import argv
def cshslp(x):
    print x
    subprocess.call(x, shell=True)
    time.sleep(2)

def getId():
    id = '0'
    while id=='0': id = random.choice(string.digits)
    id += ''.join([random.choice(string.digits + string.ascii_lowercase)  for _ in range(3)])
    print "\nPDB ID:" + id
    return id


def rcsb():
        pdbid = getId()
        cmd = "wget -nc https://files.rcsb.org/download/" + pdbid + ".pdb -P pdb"
        cshslp(cmd)

def pdbj():
        pdbid = getId()
        cmd = "wget -nc \"https://pdbj.org/rest/downloadPDBfile?format=pdb-nocompress&id=" + pdbid + "\" -O " + pdbid + ".pdb.gz && gunzip " + pdbid + ".pdb.gz ; mv " + pdbid + ".pdb pdb||rm " + pdbid + ".pdb.gz"
        cshslp(cmd)

def pdbe():
        pdbid = getId()
        cmd = "wget -nc http://www.ebi.ac.uk/pdbe/entry-files/download/pdb" + pdbid + ".ent -O ./pdb/" + pdbid + ".pdb"
        cshslp(cmd)
        if os.path.getsize('./pdb/' + pdbid + '.pdb')<1000:
            cmd  = "rm pdb/" + pdbid + ".pdb"
            cshslp(cmd)


def getPdb():
    for _ in range(0,int(argv[1])):
        rcsb()#RCSB files.rcsb.org/download/1aki.pdb pdb type:pdb
        pdbj()#PDBJ pdbj.org/rest/downloadPDBfile?format=pdb-nocompress&id=1aki type:ent.gz
        pdbe()#PDBe www.ebi.ac.uk/pdbe/entry-files/download/pdb1aki.ent type:ent
    
def main_calc(): getPdb()

if __name__ == '__main__': main_calc()
