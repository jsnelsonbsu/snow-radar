# Use a base image with Miniconda or Mambaforge
FROM condaforge/miniforge3:25.3.1-0

# copy YAML file
ADD autoterm.yml .
ADD 02_process_radargrams_wtmm.py .

# install
RUN mamba create --file autoterm.yml -y && \
	conda clean --all

ENV PATH=/opt/conda/envs/autoterm_env/bin:$PATH

RUN chmod +x /opt/conda/envs/autoterm_env/bin/python