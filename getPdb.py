
import time, subprocess, random, string, os
from sys import argv
import glob
from multiprocessing import Pool
from joblib import Parallel, delayed
from tqdm import tqdm

def rcsb(pdbid):
        if not(os.path.isfile("pdb/" + pdbid + ".pdb")):
            cmd = "wget -nc -q https://files.rcsb.org/download/" + pdbid + ".pdb -P pdb"
            subprocess.call(cmd, shell=True)

def pdbj(pdbid):
        if not(os.path.isfile("pdb/" + pdbid + ".pdb")):
            cmd = "wget -nc -q \"https://pdbj.org/rest/downloadPDBfile?format=pdb-nocompress&id=" + pdbid + "\" -O " + pdbid + ".pdb.gz && gunzip " + pdbid + ".pdb.gz ; mv " + pdbid + ".pdb pdb 2>/dev/null||rm " + pdbid + ".pdb.gz"
            subprocess.call(cmd, shell=True)

def pdbe(pdbid):
        if not(os.path.isfile("pdb/" + pdbid + ".pdb")):
            cmd = "wget -nc -q http://www.ebi.ac.uk/pdbe/entry-files/download/pdb" + pdbid + ".ent -O ./pdb/" + pdbid + ".pdb"
            subprocess.call(cmd, shell=True)
        if os.path.getsize('./pdb/' + pdbid + '.pdb')<1000:
            cmd  = "rm pdb/" + pdbid + ".pdb"
            subprocess.call(cmd, shell=True)

def getId():
    id = '0'
    while id=='0': id = random.choice(string.digits)
    id += ''.join([random.choice(string.digits + string.ascii_lowercase)  for _ in range(3)])
#    print ("\nPDB ID:" + id)
    return id

def hetatm(p):
    print(p)
    cmd = "sed -i -r 's/H(SD|SE|ID)/HIS/gI' " + p + "|sed -i -r 's/MSE/MET/gI' " + p
    subprocess.call(cmd, shell=True)
    cmd = "(less " + p + "| grep -v 'HETATM' | grep -v D[ATGC] ) > " + p + "fix.pdb"
    subprocess.call(cmd, shell=True)
    cmd = "rm " + p
    subprocess.call(cmd, shell=True)


def main():
    f = open('pdbs.txt', 'r')
    pdbs = f.readlines() # 1行毎に終端まで全て読む(改行文字も含まれる)
    f.close()
    if not os.path.exists("data"):
        os.makedirs("data")
        os.makedirs("data/pdb")
        os.makedirs("data/data")
    os.chdir("data")

    if(len(argv) <= 1):
        for i in tqdm(range(0,len(pdbs))):
            if i%3==0:rcsb(pdbs[i].strip())#RCSB files.rcsb.org/download/1aki.pdb pdb type:pdb
            if i%3==1:pdbj(pdbs[i].strip())#PDBJ pdbj.org/rest/downloadPDBfile?format=pdb-nocompress&id=1aki type:ent.gz
            if i%3==2:pdbe(pdbs[i].strip())#PDBe www.ebi.ac.uk/pdbe/entry-files/download/pdb1aki.ent type:ent
    else:
        if(argv[1].isdigit() == True):
            for i in tqdm(range(0,int(argv[1]))):
                if i%3==0:rcsb(getId())#RCSB files.rcsb.org/download/1aki.pdb pdb type:pdb
                if i%3==1:pdbj(getId())#PDBJ pdbj.org/rest/downloadPDBfile?format=pdb-nocompress&id=1aki type:ent.gz
                if i%3==2:pdbe(getId())#PDBe www.ebi.ac.uk/pdbe/entry-files/download/pdb1aki.ent type:ent
        else:
            if argv[1] == "clean":
                print("PDBファイルから塩基とHETATMを削除")
                os.chdir("pdb")
                Parallel(n_jobs=-1)([delayed(hetatm)(p) for p in glob.glob("*pdb")])
                os.chdir("../")

    os.chdir("../")

if __name__ == "__main__":
    main()
