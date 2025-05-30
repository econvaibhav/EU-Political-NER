"""Optional local transformer NER; requires the separate NER dependencies.

Uses fast-tokenizer overflow windows and retains offsets, scores, labels, model
revision, and documents with no entities. Downloads model weights on first use.
"""
import argparse
import csv
import json
from pathlib import Path


def extract(nlp, records):
    mentions=[]
    documents=[]
    for row in records:
        text=row["text"]
        predictions=nlp(text) if text.strip() else []
        kept=[]
        seen=set()
        for e in predictions:
            if e.get("entity_group") not in {"PER","ORG"}:
                continue
            span=(int(e["start"]),int(e["end"]),e["entity_group"])
            if span in seen:
                continue
            seen.add(span)
            kept.append({"record_id":f'{row["document_id"]}:{span[0]}:{span[1]}:{span[2]}',
                         "document_id":row["document_id"],"mention":text[span[0]:span[1]],
                         "start":span[0],"end":span[1],"entity_label":span[2],
                         "ner_score":float(e["score"]),"source_country":row.get("source_country","")})
        mentions.extend(kept)
        documents.append({"document_id":row["document_id"],"entity_count":len(kept),
                          "status":"entities_found" if kept else "no_entities"})
    return mentions,documents


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True,help="CSV with document_id,text,source_country")
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--model",default="FacebookAI/xlm-roberta-large-finetuned-conll03-english")
    p.add_argument("--revision",default=None,help="Use a model commit hash for reproducibility")
    p.add_argument("--stride",type=int,default=64)
    a=p.parse_args()
    if a.output_dir.exists():
        p.error("Output directory already exists; choose a new one.")
    if a.stride<0 or a.stride>=500:
        p.error("stride must be in [0,499] for the default model.")
    with a.input.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not {"document_id","text"}<=set(reader.fieldnames or []):
            p.error("Input needs document_id and text columns.")
        rows=list(reader)
    ids=[r["document_id"] for r in rows]
    if any(not x.strip() for x in ids) or len(ids)!=len(set(ids)):
        p.error("document_id must be nonempty and unique.")
    from transformers import AutoTokenizer,AutoModelForTokenClassification,pipeline
    tokenizer=AutoTokenizer.from_pretrained(a.model,revision=a.revision,use_fast=True)
    if not tokenizer.is_fast:
        p.error("Overflow handling requires a fast tokenizer.")
    model=AutoModelForTokenClassification.from_pretrained(a.model,revision=a.revision)
    nlp=pipeline("token-classification",model=model,tokenizer=tokenizer,
                 aggregation_strategy="simple",stride=a.stride,device=-1)
    mentions,documents=extract(nlp,rows)
    a.output_dir.mkdir(parents=True)
    fields=["record_id","document_id","mention","start","end","entity_label","ner_score","source_country"]
    with (a.output_dir/"mentions.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(mentions)
    metadata={"model":a.model,"requested_revision":a.revision,
              "resolved_revision":getattr(model.config,"_commit_hash",None),
              "stride":a.stride,"documents":documents}
    (a.output_dir/"extraction_report.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    print(f"Extracted {len(mentions)} mentions from {len(documents)} documents.")
