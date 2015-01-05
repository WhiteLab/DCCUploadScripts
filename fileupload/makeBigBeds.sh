#!bin/bash
#usage : sh makeBigBeds.sh <directory name>
#converts all bed files in directory $1 to bigBeds
for filename in $1/*.bed; do
    echo "processing $filename..."
    awk -F, '{$1="chr"$1;print $0}' OFS=, $filename | sed 's/chrdmel_mitochondrion_genome/chrM/g'  | sort -k1,1 -k2,2n >  $filename.chr.bed
    bedToBigBed $filename.chr.bed /raid/modencode/DCC/fileupload/encValData/dm3/chrom.sizes "${filename%%.bed}.bb"
    rm $filename.chr.bed
    echo " $filename converted to BigBed"
done
