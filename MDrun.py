# GROMACS 5.1.4 DINAMICS RUN #
# Santos, Leonardo #
# May 2017#

# IMPORTS #
import os
import sys

#DATA DEFINITION#

Extension = ".pdb"
Header = "#!/bin/bash\n#$ -cwd\n#$ -pe orte 8 #number of cores\n#$ -e gromacs.err   # redirections for stdout.err\n#$ -o gromacs.log\n#$ -q fila2.q\n\nexport I_MPI_FABRICS=shm:ofa\n\n"
GromacsLocal = "/usr/local/gromacs/bin/gmx "
ServerStart = "mpirun -np 1 /usr/local/gromacs_local/bin/gmx_local "
Local = os.getcwd()

# DATA INPUT #
PdbFile = raw_input("PDB File: ")
if Extension not in PdbFile: #in case the user doesn't specify the file's extension
	PdbFile += Extension

StandardName = raw_input("Standard output name: ")

# OPTION INPUT #
f=open("input1.txt","w")
f.write("13\n") #creates a input file to select SOL to add charges
f.close()

def GetCharge (FileName): #gets charge variation
	ch = open(FileName,"r")
	for line in ch:
		if "  System has non-zero total charge: " in line:
			if ": -" in line:
				ncharge = line.replace("  System has non-zero total charge: -","")[0]
				charge = 0
			else:
				ncharge = line.replace("  System has non-zero total charge: ","").replace("\n","")
				charge = 1
	return charge,int(ncharge[0])


def FilePrep (PDB,Standard): #creates a script that can be run on SBCB server
	os.system("\n"+GromacsLocal+"pdb2gmx -f "+PDB+" -o "+Standard+".gro -i "+Standard+".itp -p "+Standard+".top -ignh -ff gromacs54e7 -water spc")
	os.system("\n"+GromacsLocal+"editconf -f "+Standard+".gro -o "+Standard+"_box.gro -c -bt dodecahedron -d 1.0")
	os.system("\n"+GromacsLocal+"solvate -cp "+Standard+"_box.gro -o "+Standard+"_sol.gro -p "+Standard+".top -cs")
	os.system("\n"+GromacsLocal+"grompp -f em_steep.mdp -c "+Standard+"_sol.gro -p "+Standard+".top -o "+Standard+"_min.tpr")
	os.system("\n"+GromacsLocal+"mdrun -v -s "+Standard+"_min.tpr -deffnm "+Standard+"_min")
	os.system("\n"+GromacsLocal+"grompp -f ions.mdp -c "+Standard+"_min.gro -p "+Standard+".top -o "+Standard+"_genion.tpr > "+Standard+"charge.txt 2>&1")
	charge= GetCharge(Standard+"charge.txt")
	if (charge[0]==0): #in case its a negative charge
		os.system("\n"+GromacsLocal+"genion -s "+Standard+"_genion.tpr -o "+Standard+"_ions.gro -np "+str(charge[1])+" -pname NA -pq +1 -p "+Standard+".top < input1.txt")
	if (charge[0]==1):
		os.system("\n"+GromacsLocal+"genion -s "+Standard+"_genion.tpr -o "+Standard+"_ions.gro -nn "+str(charge[1])+" -nname CL -nq -1 -p "+Standard+".top < input1.txt")

FilePrep(PdbFile,StandardName)
