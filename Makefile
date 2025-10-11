DATA_DIR ?= ./data
TMP_DIR ?= /tmp
NTHREADS ?= $(shell nproc)
MRIQC_DIR = $(DATA_DIR)/derivatives/mriqc

.PHONY: build-container run-pipeline run-pipeline-no-docker run-qc mriqc-participant mriqc-group

build-container:
	docker compose build

run-pipeline:
	docker compose run --rm ms-tissue-seg

run-pipeline-no-docker:
	uv run python run_pipeline.py

run-qc: mriqc-participant mriqc-group

mriqc-participant:
	mkdir -p $(MRIQC_DIR)
	docker run --rm \
		-v $(DATA_DIR)/bids_input:/data:ro \
		-v $(MRIQC_DIR):/out \
		nipreps/mriqc:latest \
		/data /out participant \
		-w $(TMP_DIR) \
		--nprocs $(NTHREADS) \
		--no-sub

mriqc-group:
	docker run --rm \
		-v $(DATA_DIR)/bids_input:/data:ro \
		-v $(MRIQC_DIR):/out \
		nipreps/mriqc:latest \
		/data /out group \
		-w $(TMP_DIR) \
		--nprocs $(NTHREADS) \
		--no-sub