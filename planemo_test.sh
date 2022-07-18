#!/bin/sh


## **@AUTHOR**: Lain Pavot - lain.pavot@inrae.fr
## **@DATE**: 22/06/2022

VENV=.venv
TEST_DIR=/tmp/history_metadata_extractor

if [ ! -d ".venv" ];then
  python3 -m virtualenv ${VENV} ;
fi


. ${VENV}/bin/activate

if [ "$(which planemo)" = "" ];then
   pip install planemo ;
fi


if [ ! -d "${TEST_DIR}" ];then
  planemo conda_install --conda_prefix ${TEST_DIR} . ;
fi

planemo lint --fail_level error ./*.xml || exit 255 ;

planemo test \
  --install_galaxy \
  --conda_dependency_resolution \
  --conda_prefix ${TEST_DIR} \
  --no_cleanup \
  --no_wait \
  --simultaneous_uploads \
  ${TEST_FLAGS} \
  history_metadata_extractor.xml \
;
