#!/bin/bash



## **@AUTHOR**: Lain Pavot - lain.pavot@inrae.fr
## **@DATE**: 22/06/2022


envs_directory=$(pwd)
envs_directory=/tmp/history_metadata_extractor-envs
mkdir -p ${envs_directory}

VENV=${envs_directory}/.manual-venv
CENV=${envs_directory}/.manual-conda

MAMBA_SOLVER=
## comment to deactivate mamba solver
MAMBA_SOLVER="--experimental-solver libmamba"

ENV_NAME=history_metadata_extractor
XML_PATH=./history_metadata_extractor.xml
SCRIPT_NAME=history_metadata_extractor.py
output_name=out.html
options=" \
  -d ./test-data/datasets_attrs.txt \
  -j ./test-data/jobs_attrs.txt \
  -o ./${output_name} \
"
expected_result=test-data/out.html
runner=python3.10
dependencies=python=3.10.5
miniconda_version=py37_4.12.0-Linux-x86_64



if [ ! -e "${VENV}" ];then
  echo "virtualenv not created yet, creating..."
  python3 -m virtualenv "${VENV}"
  echo "venv created"
else
  echo "virtualenv already exist: ok"
fi
. ${VENV}/bin/activate

if [ ! -e "${CENV}" ];then
  echo "conda env not created yet, creating..."
  if [ ! -e ./install_conda.sh ];then
    wget \
      -O install_conda.sh \
      https://repo.anaconda.com/miniconda/Miniconda3-${miniconda_version}.sh \
    ;
  fi
  bash ./install_conda.sh -b -p "${CENV}"

  ${CENV}/bin/conda install -y -n base conda-libmamba-solver
  ${CENV}/bin/conda create \
    -y \
    --quiet \
    --override-channels \
    --channel conda-forge \
    --channel bioconda \
    --channel defaults \
    --name "${ENV_NAME}" \
    ${MAMBA_SOLVER} \
    ${dependencies}
  echo "conda env created"
fi

echo ""
echo "===== preparing ====="

oldwd=$(pwd)
tmp=$(mktemp -d)
echo "Working in ${tmp}"
files=$(find . -maxdepth 1 -regex "./.+")
cd "${tmp}"
echo "creating links..."
echo "${files}" | xargs -I file ln -s "${oldwd}"/file file
echo "ready to work"

echo ""
echo "===== processing ====="

. "${CENV}/bin/activate" "${CENV}/envs/${ENV_NAME}" ;

${runner} ./${SCRIPT_NAME} ${options};

echo ""
echo "Error code: ${?}" ;

lines=$(diff "${output_name}" "${expected_result}" 2>&1)

echo ""
echo "===== results ====="

if [ "${lines}" = "" ];then
  echo "Result equal to expected."
else
  echo "Some lines are different:"
  echo "${lines}"
fi

echo ""
echo "===== cleaning ====="

echo "Removing ${tmp}..."
rm -rf "${tmp}"

echo ""
echo "Done."
