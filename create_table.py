# Pulls out relevant data from a DB query that is supplied to it
def Var_Table(vars, assembly_spec=None):
    display = []
    for var in vars:
        for assembly in var["mappings"]:
            if "clinical_significance" in var:
                clin_sig = ", ".join([x for x in var["clinical_significance"]])
            else:
                clin_sig="N/A"
            if assembly_spec==None or assembly["assembly_name"]==assembly_spec:
                display.append({"seq_region_name":f'chr{assembly["seq_region_name"]}',
                                    "start":assembly["start"],
                                    "end":assembly["end"],
                                    "assembly_name":assembly["assembly_name"],
                                    "allele_string":assembly["allele_string"],
                                    "name":var["name"],
                                    "most_severe_consequence":var["most_severe_consequence"],
                                    "synonyms":[syn for syn in var["synonyms"]],
                                    "MAF":var["MAF"],
                                    "evidence":", ".join([x for x in var["evidence"]]) if len(var["evidence"]) > 0 else "N/A",
                                    "clinical_significance":clin_sig})
    return display
