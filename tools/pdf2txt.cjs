const fs=require('fs');const pdf=require('pdf-parse');
const file=process.argv[2],out=process.argv[3];
pdf(fs.readFileSync(file),{pagerender:p=>p.getTextContent().then(t=>{let last=null,s='';for(const it of t.items){if(last&&Math.abs(last.transform[5]-it.transform[5])>2)s+='\n';else if(last&&it.transform[4]-(last.transform[4]+last.width)>8)s+=' ';s+=it.str;last=it;}return s+'\n\f';})}).then(d=>{fs.writeFileSync(out,d.text);console.log('pages',d.numpages,'chars',d.text.length);});
