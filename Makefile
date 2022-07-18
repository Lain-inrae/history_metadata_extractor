

## **@AUTHOR**: Lain Pavot - lain.pavot@inrae.fr
## **@DATE**: 22/06/2022


test:
	python3 ./history_metadata_extractor.py \
		-d ./test-data/datasets_attrs.txt \
		-j ./test-data/jobs_attrs.txt \
		-o ./test-data/result.html \
	;
	firefox ./test-data/result.html

