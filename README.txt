EXECUTE:
Go to a UNIX-based terminal (or python compiler) and enter:

>>> python final_proj.py

The code will automatically pull data from a command file:
cmd_text.txt (included inside this ZIP file)

OUTPUT:
The terminal will show any hazard dependcy violations, and
values stored in memory (SRAM).

FILES CREATED:
<Please Note>: Generated files may not appear to have proper formatting
when opened using the standard "notepad". If you open the text file in any
other text editor (e.g. notepad++, sublime), the formatting will
be properly formatted.

A file: golden_results.txt , will be generated and show the 
verilogA compilation results.

Additionally, the vector file: cpu.vec  , will be generated and can
be used in any Cadence simulation. 

The python will generate two intermediate files, one called cmd2.txt
and the other called new_cmd.txt. Both can be deleted, as cmd2.txt
cleans the original text file and new_cmd.txt shows the hazard detection 
results.

