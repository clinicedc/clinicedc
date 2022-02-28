from .lab import AliquotType

bc = AliquotType(name="Buffy Coat", alpha_code="BC", numeric_code="12")
fbc = AliquotType(name="FBC", alpha_code="FBC", numeric_code="63")
pl = AliquotType(name="Plasma", alpha_code="PL", numeric_code="36")
qfc = AliquotType(name="Quantitative FC", alpha_code="QFC", numeric_code="61")
serum = AliquotType(name="Serum", alpha_code="SERUM", numeric_code="06")
sputum = AliquotType(name="Sputum", alpha_code="SPUTUM", numeric_code="07")
urine = AliquotType(name="Urine", alpha_code="UR", numeric_code="08")
wb = AliquotType(name="Whole Blood", alpha_code="WB", numeric_code="02")

# CSF
csf_store = AliquotType(name="CSF store", alpha_code="CSF", numeric_code="62")
csf_testing = AliquotType(name="Isolates", alpha_code="ISOLATES", numeric_code="64")
csf_glucose = AliquotType(name="Glucose", alpha_code="GLUCOSE", numeric_code="65")
csf_protein = AliquotType(name="Protein", alpha_code="PROTEIN", numeric_code="66")
csf_pellet = AliquotType(name="CSF Pellet", alpha_code="PELLET", numeric_code="67")
csf_supernatant = AliquotType(
    name="CSF Supernatant", alpha_code="SUPERNATANT", numeric_code="68"
)
csf = AliquotType(name="Cerebro Spinal Fluid", alpha_code="CSF", numeric_code="56")
tissue_biopsy = AliquotType(name="Tissue biopsy", alpha_code="TISSUE", numeric_code="44")


# dummy
disposable = AliquotType(name="Disposable", alpha_code="XX", numeric_code="00")


wb.add_derivatives(bc, pl, serum, fbc, wb)
sputum.add_derivatives(sputum)
urine.add_derivatives(urine)
