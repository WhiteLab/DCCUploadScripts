#!bin/baxh
#usage : sh addchrtobam.sh <directory name>
#makes a copy of  bam files in directory $1 to <filename>.nochr.bam
#converts all bam files in directory $1 to sam, adds chr, converts them back to bam
for filename in $1/*.bam; do

    fn=$(basename "$filename")
    echo "processing $filename..."
    #get file name without extension
    #fnamenoext="${filename##*/}"
    echo " copying as ${filename%%.bam}.nochr.bam"     
    cp $filename "${filename%%.bam}.nochr.bam" &
    wait
    samtools view -h "${filename%%.bam}.nochr.bam" | awk 'BEGIN{FS=OFS="\t"} (/^@/ && !/@SQ/){print $0} $2~/^SN:[1-9]|^SN:X|^SN:Y|^SN:M/{print $0}  $3~/^[1-9]|X|Y|M/{$3="chr"$3; print $0} ' | sed 's/SN:/SN:chr/g' | sed 's/dm3.nochr/dm3.chr/g' | samtools view -bS - > $filename
    echo " added chr to $filename"
done
