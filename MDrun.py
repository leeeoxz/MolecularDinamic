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
ServerStartLocal = "mpirun -np 1 /usr/local/gromacs_local/bin/gmx_local "
ServerStartMpi = "mpirun -np 1 /usr/local/gromacs_mpi/bin/gmx_mpi "
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
	print charge,ncharge[0]
	return charge,int(ncharge[0])

def WriteTxt (standard):
	f= open("Script.sh","w")
	f.write(Header)
	f.write(ServerStartLocal+"grompp -f nvt.mdp -c "+standard+"_ions.gro -o "+standard+"_nvt.tpr -p "+standard+"5000.top -maxwarn 1\n")
	f.write(ServerStartMpi+"mdrun -nt 8 -v -s "+standard+"_nvt.tpr -deffnm "+standard+"_nvt\n")
	f.write(ServerStartLocal+"grompp -f npt_relax4000.mdp -c "+standard+"_nvt.gro -o "+standard+"_npt_4000.tpr -p "+standard+"4000.top -t "+standard+"_nvt.cpt -maxwarn 1\n")
	f.write(ServerStartMpi+"mdrun -nt 8 -v -s "+standard+"_npt_4000.tpr -deffnm "+standard+"_npt_4000\n")
	f.write(ServerStartLocal+"grompp -f npt_relax3000.mdp -c "+standard+"_npt_4000.gro -o "+standard+"_npt_3000.tpr -p "+standard+"3000.top -t "+standard+"_npt_4000.cpt -maxwarn 1\n")
	f.write(ServerStartMpi+"mdrun -nt 8 -v -s "+standard+"_npt_3000.tpr -deffnm "+standard+"_npt_3000\n")
	f.write(ServerStartLocal+"grompp -f npt_relax2000.mdp -c "+standard+"_npt_3000.gro -o "+standard+"_npt_2000.tpr -p "+standard+"2000.top -t "+standard+"_npt_3000.cpt -maxwarn 1\n")
	f.write(ServerStartMpi+"mdrun -nt 8 -v -s "+standard+"_npt_2000.tpr -deffnm "+standard+"_npt_2000\n")
	f.write(ServerStartLocal+"grompp -f npt_relax1000.mdp -c "+standard+"_npt_2000.gro -o "+standard+"_npt_1000.tpr -p "+standard+"1000.top -t "+standard+"_npt_2000.cpt -maxwarn 1\n")
	f.write(ServerStartMpi+"mdrun -nt 8 -v -s "+standard+"_npt_1000.tpr -deffnm "+standard+"_npt_1000\n")
	f.write(ServerStartLocal+"grompp -f npt_prod_0-10ns.mdp -c "+standard+"_npt_1000.gro -o "+standard+"_prod_0-10ns.tpr -p "+standard+"1000.top -t "+standard+"_npt_relax1000.cpt -maxwarn 1\n")
	f.write(ServerStartMpi+"mdrun -nt 8 -v -s "+standard+"_prod_0-10ns.tpr -deffnm "+standard+"_prod_0-10ns\n")
	f.close()

def writeItpTop(standard):
	for i in range(1000,6000,1000):
		file = open(standard+".itp","r")
		wri = open(standard+str(i)+".itp","w")
		for line in file:
			line = line.replace("1000  1000  1000",str(i)+"  "+str(i)+"  "+str(i))
			wri.write(line)
		file = open(standard+".top","r")
		writop = open(standard+str(i)+".top","w")
		for line in file:
			line = line.replace(standard+".itp",standard+str(i)+".itp")
			writop.write(line)



def FilePrep (PDB,Standard): #creates a script that can be run on SBCB server
	os.system("\n"+GromacsLocal+"pdb2gmx -f "+PDB+" -o "+Standard+".gro -i "+Standard+".itp -p "+Standard+".top -ignh -ff gromos54a7 -water spc")
	os.system("\n"+GromacsLocal+"editconf -f "+Standard+".gro -o "+Standard+"_box.gro -c -bt dodecahedron -d 1.0")
	os.system("\n"+GromacsLocal+"solvate -cp "+Standard+"_box.gro -o "+Standard+"_sol.gro -p "+Standard+".top -cs")
	os.system("\n"+GromacsLocal+"grompp -f em_steep.mdp -c "+Standard+"_sol.gro -p "+Standard+".top -o "+Standard+"_min.tpr")
	os.system("\n"+GromacsLocal+"mdrun -v -s "+Standard+"_min.tpr -deffnm "+Standard+"_min")
	os.system("\n"+GromacsLocal+"grompp -f ions.mdp -c "+Standard+"_min.gro -p "+Standard+".top -o "+Standard+"_genion.tpr > "+Standard+"charge.txt 2>&1")
	charge = GetCharge(Standard+"charge.txt")
	if (charge[0]==0): #in case its a negative charge
		os.system("\n"+GromacsLocal+"genion -s "+Standard+"_genion.tpr -o "+Standard+"_ions.gro -np "+str(charge[1])+" -pname NA -pq +1 -p "+Standard+".top < input1.txt")
	if (charge[0]==1):
		os.system("\n"+GromacsLocal+"genion -s "+Standard+"_genion.tpr -o "+Standard+"_ions.gro -nn "+str(charge[1])+" -nname CL -nq -1 -p "+Standard+".top < input1.txt")
	writeItpTop(Standard)
	WriteTxt(Standard)
FilePrep(PdbFile,StandardName)
