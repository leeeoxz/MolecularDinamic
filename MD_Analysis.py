import os

standard = raw_input("Protein ID: ") #gets the standard name to output files.

GromacsLocal = "/usr/local/gromacs/bin/gmx "
f=open("input1.txt","w")
f.write("1\n")
f.close()
f=open("input2.txt","w")
f.write("20\n")
f.write("15\n")
f.write("21\n")
f.write("13\n")
f.write("12\n")
f.write("10\n")
f.write("11\n")
f.write("\n")
f.close()
f=open("input3.txt","w")
f.write("3\n")
f.write("3\n")
f.close()

def Analysis (standard):
	os.system("\n"+GromacsLocal+"eneconv -f "+standard+"_prod_0-10ns.edr "+standard+"_prod_10-50ns.edr -o "+standard+"_prod_0-50ns.ene")
	os.system("\n"+GromacsLocal+"trjcat -f "+standard+"_prod_0-10ns.trr "+standard+"_prod_10-50ns.trr -o "+standard+"_prod_0-50ns.xtc")
	os.system("\n"+GromacsLocal+"gyrate -f "+standard+"_prod_0-50ns.xtc -s "+standard+"_npt_1000.tpr -o "+standard+"_gyrate.xvg < input1.txt")
	os.system("\n"+GromacsLocal+"rmsf -f "+standard+"_prod_0-50ns.xtc -s "+standard+"_npt_1000.tpr -o "+standard+"_rmsf.xvg < input1.txt")
	os.system("\n"+GromacsLocal+"energy -f "+standard+"_prod_0-50ns.ene -s "+standard+"_npt_1000.tpr -o "+standard+"_energy.xvg < input2.txt")
	os.system("\n"+GromacsLocal+"rms -f "+standard+"_prod_0-50ns.xtc -s "+standard+"_npt_1000.tpr -o "+standard+"_rms.xvg < input3.txt")

Analysis(standard)
