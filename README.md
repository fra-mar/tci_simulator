# Target gontrolled infusion pump for anesthesia delivery.<br> A simulator.

Anesthesia delivery methods can be roughly divided in two groups: inhalational and intravenous.
When only intravenous anesthesia is administered the term *Total IntraVenous Anesthesia* (TIVA) is commonly used.
>The pharmacokinetics of these drugs can be described best with a three-compartment model. 
The nature of a multicompartment model makes difficult both to hold a constant effect site or plasma concentration with a fast
infusion rate and stimate the drug concentration at the effect site. 
<br>Several models are available for propofol, remifentanyl and sufentanyl, probably the most commonly used drugs of this kind. 
Those models are programmed in commercially available pumps and allow the anesthesiologist to program the target, i.e., the desired concentration at
the effect site or in the plasma, hence the term *Target Controlled Infusion* (TCI).

Some time ago I wondered how did a TCI pump manage to know how much medication should it administer to reach exactly the desired target concentration so
I searched the literature and programmed this simulator in Python.

In that journey I wrote shorter scripts to understand both the pharmacology and the coding. 

### /definitive/CCIP 
The script tci_sim is the "main menu". There drug-model, patient characteristics can be chosen. 

### /definitive/fast_infRate_....
The folder contains a script that shows what happens to the plasma concentration when propofol is adminstered at a fast infusion rate.
It's based on Schnider's model. This model is not reliable when the patients *body mass index* is above 31  $Kg\ m^{2}$ and therefore commercial pumps have limits for weight and height. This script illustrates this deffect, resulting in lower concentrations than expected with low heights and high weights.

### /definitive/caffeine.py
I wrote it to understand how it works with a monocompartimental drug... with the fun of talking about coffee. 
I added the possibility to adjust the microvariables: quite often only central values are used, but most people are not the "mean" or "median" value.

### /definitive/decay.py
Pharmacokinetics is all about exponential decay. 
The script shows three exemples and the relation among three commonly used variables that describe the process.

### /tests
Some selected script I wrote when developing the simulator.
