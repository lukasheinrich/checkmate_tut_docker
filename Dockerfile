FROM lukasheinrich/checkmate_vm
RUN /usr/bin/wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py && pip install click
ADD utility_scripts /checkmate_util
ADD checkmate_templates /templates
ENV PATH=/checkmate_util:$PATH
WORKDIR /checkmate_util
