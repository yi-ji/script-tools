# execute this script every short interval using crontab
# ethminer is renamed as 'em'

miner_config="put yours"

function run_em()
{
	nohup ./em -S $miner_config > em.log &
    echo `date`: start
}

function run_em_half()
{
	nohup ./em --cuda-devices $1 $miner_config > em.log &
	echo `date`: start on gpu $1 only
}

function kill_em()
{
        kill -9 `pgrep -x em`
        echo `date`: quit
}

function check_gpu()
{
	all_proc=`nvidia-smi -i $1 | grep MiB | awk '{print $6;}' | grep MiB | wc -l`
	em_proc=`nvidia-smi -i $1 | grep -e "\.\/em.*MiB" | wc -l`

	if [ $all_proc -eq 0 ]
	then
		eval gpu_$1=hima
	elif [ $em_proc -ge 1 ]
	then
		eval gpu_$1=mining
		if [ $all_proc -gt $em_proc ]
		then
			eval gpu_$1=busy
		fi
	fi
}

function start_gpu()
{
	if [[ $gpu_0 == hima ]]
        then
                run_em_half 0
        fi
        if [[ $gpu_1 == hima ]]
        then
                run_em_half 1
        fi
}

gpu_0=other
gpu_1=other

check_gpu 0
check_gpu 1

if [[ $gpu_0 == hima && $gpu_1 == hima ]]
then
	run_em
elif [[ $gpu_0 == busy || $gpu_1 == busy ]]
then
	kill_em
	check_gpu 0
	check_gpu 1
	start_gpu
elif [[ ($gpu_0 == hima && $gpu_1 == mining) || ($gpu_0 == mining && $gpu_1 == hima) ]]
then
	kill_em
	run_em
else
	start_gpu
fi