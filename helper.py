from pymongo import MongoClient
import urllib.request as request
import json

# Dict of reference genomes, used in the forms for searching and inputting new variants.
# Adding a new reference here, should just work and slot in everywhere.
# Dict is used to convert from the key from a search form to the actual reference genome
Constants={"assembly":{1:"GRCh37",2:"GRCh38"}}

#Set up your DB Connection here, currently set for a local instance
def Database():
    client = MongoClient(port=27017)
    db = client.variants
    return db.variants



def Clean_Search(query):
    difficult_keys = {"chr":"mappings.seq_region_name",
                      "assembly":"mappings.assembly_name"}
    # Translates between form values and 'real' values using the Constants Dictionary
    # E.G the form provides a value of 2 for GRCh38, this changes the assembly to be GRCh38
    for k, v in query.items():
        if k in Constants.keys():
            query[k] = Constants[k][v]#
    # Changes between things like "assebmly" and "mappings.assembly_name" as it's nested in mappings 
    to_del = []
    to_add = []
    for k, v in list(query.items()):
        for dk, dv in list(difficult_keys.items()):
            if k==dk:
                value = v
                del(query[k])
                query[dv]=v
    # Changes "start" from search form to mappings.start and mappings.end 
    # only checks for start because form has a validation on it so if end provided, start must be and vice-versa
    if "start" in query.keys():
        start_value=query["start"]
        end_value=query["end"]
        del(query["start"])
        del(query["end"])
        query["mappings.start"]={"$gte": int(start_value)}
        query["mappings.end"]={"$lte": int(end_value)}
    return query

def Clean_Form(form):
    #removes extra information from the dict so only search query data is sent
    del(form["search"])
    del(form["cancel"])
    del(form["csrf_token"])
    # finds and removes blank fields, otherwise search filter later gets messed up
    # list() used to make a copy, as otherwise you get a RunTimeError, Dictionary changed size during iteration
    for k,v in list(form.items()):
        if v is None or v=="":
            del(form[k])
    return form
    
# NEEDS TIDYING UP AND SORTING OUT, WAS DONE IN A RUSH!    
def Add_Variant(dsID):
    try:
        db = Database()
        ID=dsID.strip("rs")
        url=f"https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{ID}"
        response=json.loads(request.urlopen(url).read())
        # mappings: {0: {location: chr:start-end, assembly_name: GRCh38, end: end, 
        # seq_region_name: chr, strand:int, coord_system: chromosome, allele_string: Ref/Alt, start:start}}
        # name: rs number
        # MAF: MAF
        # var_class: snp etc...
        # synonyms: [HGVSc etc...]
        # evidence: [sources]
        # most_severe_consequence : intron_variant etc...
        to_ins = {}
        sources=[]
        to_ins["source"]="Variants (including SNPs and indels) imported from dbSNP"
        to_ins["mappings"]=[]
        for i, val in enumerate(response["primary_snapshot_data"]["placements_with_allele"]):
            try:
                ref_genome=val["placement_annot"]["seq_id_traits_by_assembly"][0]["assembly_name"].split(".")[0]
                temp={}
                chr="".join([x for x in val["seq_id"].split(".")[0] if x.isdigit()]).strip("0")
                for al in val["alleles"]:
                    if al["allele"]["spdi"]["deleted_sequence"]!=al["allele"]["spdi"]["inserted_sequence"]:
                        ref=al["allele"]["spdi"]["inserted_sequence"]
                        alt=al["allele"]["spdi"]["deleted_sequence"]
                        coords=al["hgvs"].split(".")[-1].split("_")
                        if len(coords)==1:
                            start="".join([x for x in coords[0] if x.isdigit()])
                            end="".join([x for x in coords[0] if x.isdigit()])
                        else:
                            start="".join([x for x in coords[0] if x.isdigit()])
                            end="".join([x for x in coords[1] if x.isdigit()]) 
                        start=int(start)
                        end=int(end)                   
                temp["location"]=f"{chr}:{start}-{end}"
                temp["assembly_name"]=ref_genome
                temp["end"]=end
                temp["seq_region_name"]=chr
                temp["coord_system"]="chromosome"
                temp["allele_string"]=f"{ref}/{alt}"
                temp["start"]=start
                to_ins["mappings"].append(temp)
                print(i)
            except Exception as e:
                continue
        to_ins["MAF"]=None
        for freq in response["primary_snapshot_data"]["allele_annotations"][0]["frequency"]:
            if freq["study_name"]=="1000Genomes":
                sources.append("1000Genomes")
                maf=((freq["total_count"]-freq["allele_count"])/freq["total_count"])
                to_ins["MAF"]=maf
        to_ins["name"]=dsID    
        to_ins["var_class"]=response["primary_snapshot_data"]["variant_type"]
        url2=f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=snp&id={ID}&format=json"
        response2=json.loads(request.urlopen(url2).read())
        to_ins["most_severe_consequence"]=response2["result"][ID]["fxn_class"].split(",")[0]
        to_ins["synonyms"]=["TO DO LATER..."]
        to_ins["evidence"]=sources
        db.insert_one(to_ins)
        return True
    except:    
        return False
