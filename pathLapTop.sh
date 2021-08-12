export KALDI_ROOT=/home/eschng/ces_work/kaldi
export SRILM_ROOT=$KALDI_ROOT/tools/srilm/bin/i686-m64
export SCLITE_ROOT=$KALDI_ROOT/tools/sctk-20159b5/bin
export PATH=$PWD/utils/:$KALDI_ROOT/tools/openfst/bin:$SRILM_ROOT:$SCLITE_ROOT:$PWD:$PATH
[ ! -f $KALDI_ROOT/tools/config/common_path.sh ] && echo >&2 "The standard file $KALDI_ROOT/tools/config/common_path.sh is not present -> Exit!" 
. $KALDI_ROOT/tools/config/common_path.sh && echo 'ok1'
export LC_ALL=C
