# crontab this script

all_gpu=(0 1 2 3)
hima_gpu=()
mapping=(1 2 0 3) # smi->cuda, 0123->1203

function check_gpu()
{
	all_proc=`nvidia-smi -i $1 | grep MiB | awk '{print $6;}' | grep MiB | wc -l`
	em_proc=`nvidia-smi -i $1 | grep -e "\.\/em.*MiB" | wc -l`

	if [ $all_proc -eq 0 ]
	then
		hima_gpu+=($1)
	elif [[ $em_proc -ge 1 && $all_proc -gt $em_proc ]]
	then
		pid=`nvidia-smi -i $1 | grep -e "\.\/em.*MiB" | awk '{print $3;}'`
		kill -9 $pid
		echo `date`: stop on gpu $1
	fi
}

for gpu_i in "${all_gpu[@]}"
do
	check_gpu $gpu_i
done

if [ ${#hima_gpu[@]} -gt 0 ]
then
	echo `date`: start on gpu "${hima_gpu[@]}"
	for i in $(seq 0 $((${#hima_gpu[@]}-1)))
	do
		gpu_i=${hima_gpu[$i]}
		hima_gpu[$i]=${mapping[$gpu_i]}
	done
	nohup ./miner $your_config &
fi