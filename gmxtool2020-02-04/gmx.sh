#------------------
box="2.0"
ion1="K"
ion2="CL"
gpu="01"
mpi="1"
omp="8"
#$ -pe ompi 8
#$ -q allquincy.q
#$ -N hoge0
#------------------

#$ -cwd
#$ -S /bin/bash
#$ -p -100
#$ -j y
export OMP_NUM_THREADS=${omp}

mkdir -p {log,rmsd}

for x in pdb/*.pdb; do
  x=${x##*/}
  x=${x%%.*}

  mkdir ${x}; cd $_
  mkdir -p {minim,em,nvt,npt}
  cp {../mdp/*ions*,../mdp/*minim*} minim
  cp ../mdp/*nvt* em
  cp ../mdp/*npt* nvt
  cp ../mdp/md* npt

  if test -e "md_0_1.trr"; then
    echo "中断したファイル:md_0_1.trr"
    date -r "md_0_1.trr"
    echo "再開しますか？[y/n]"
    read menu
    if [ $menu = "y" ]; then
      gmx mdrun -v -deffnm md_0_1 -cpi md_0_1_prev.cpt -ntmpi $mpi -ntomp $omp -gpu_id $gpu
    else
      echo "No:md_0_1.trrを削除or移動してください"
      sleep 2
    fi
  else

    cd minim

    gmx pdb2gmx -f ../../pdb/${x}.pdb -o ${x}.gro -ignh -water spce <<EOF
    4
EOF

    mv ../../pdb/${x}.pdb ../../log


    gmx editconf -f ${x}.gro -o ${x}_newbox.gro -c -d ${box} -bt cubic
    gmx solvate -cp ${x}_newbox.gro -cs spc216.gro -o ${x}_solv.gro -p topol.top
    gmx grompp -maxwarn 10 -f ions.mdp -c ${x}_solv.gro -p topol.top -o ions.tpr
    gmx genion -s ions.tpr -o ${x}_solv_ions.gro -p topol.top -conc 0.15 -pname ${ion1} -nname ${ion2} <<EOF
    13
EOF
    gmx grompp -maxwarn 10 -f minim.mdp -c ${x}_solv_ions.gro -p topol.top -o em.tpr
    gmx mdrun -v -deffnm em -ntmpi $mpi -ntomp $omp -gpu_id $gpu

    mv {em*,topol.top,posre.itp} ../em; cd $_
    gmx grompp -maxwarn 10 -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr
    gmx mdrun -v -deffnm nvt -ntmpi $mpi -ntomp $omp -gpu_id $gpu

    mv {nvt*,topol.top,posre.itp} ../nvt; cd $_
    gmx grompp -maxwarn 10 -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr
    gmx mdrun -v -deffnm npt -ntmpi $mpi -ntomp $omp -gpu_id $gpu

    mv {npt*,topol.top,posre.itp} ../npt; cd $_
    gmx grompp -maxwarn 10 -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md_0_1.tpr
    gmx mdrun -v -deffnm md_0_1 -ntmpi $mpi -ntomp $omp -gpu_id $gpu

    mv md* ../; cd $_

    gmx trjconv -f md_0_1.xtc -s md_0_1.tpr -pbc nojump -o md_0_1_nojump.xtc <<EOF
    0 0
EOF
    gmx trjconv -f md_0_1_nojump.xtc -s md_0_1.tpr -center -o md_0_1_nojump_center.xtc  <<EOF
    0 0
EOF
    gmx trjconv -f md_0_1_nojump_center.xtc -s md_0_1.tpr -pbc mol -ur rect -o md_0_1_fix.xtc <<EOF
    0 0
EOF
    rm md_0_1_nojump*

    gmx rms -s md_0_1.tpr -f md_0_1_fix.xtc -o "${x}_rmsd" -tu ns <<EOF
    4 4
EOF
    sed -e "s/    /,/g" -e "s/   /  /g" -ne '19,$p' "${x}_rmsd.xvg" > ../rmsd/"${x}_rmsd.csv"

  fi
cd ../
done
