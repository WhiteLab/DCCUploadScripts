#!bin/bash
#usage : sh makeBigWigs.sh <directory name>
#converts all wig files in directory $1 to bigWigss
for filename in $1/*.wig; do
    echo "processing $filename..."
    awk -F, '{$1="chr"$1;print $0}' OFS=, $filename | sed 's/chrdmel_mitochondrion_genome/chrM/g' | sed '/^chrtrack/d' > $filename.chr.wig    
    # -clip option to issue warning messages rather than dying if wig file contains items off end of chromosome. 
    # some wig files had chr3RHet extending more than listed in chrom.sizes
    wigToBigWig -clip $filename.chr.wig /raid/modencode/DCC/fileupload/encValData/dm3/chrom.sizes "${filename%%.wig}.bw"
    rm $filename.chr.wig
    echo " $filename converted to BigWig"
done
