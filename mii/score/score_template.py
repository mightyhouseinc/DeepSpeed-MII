# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: Apache-2.0

# DeepSpeed Team

# flake8: noqa
import os
import json
import time
import torch

import mii

model = None


def init():
    global mii_config
    mii_config = mii.config.MIIConfig(**mii_config)

    start_server = (
        not mii.utils.is_aml() or os.getpid() % mii_config.replica_num == 0
    )
    if start_server:
        mii.backend.MIIServer(mii_config)

    global model
    model = None

    # In AML deployments both the GRPC client and server are used in the same process
    if mii.utils.is_aml():
        model = mii.backend.MIIClient(mii_config=mii_config)


def run(request):
    global mii_config, model
    assert (
        model is not None
    ), "grpc client has not been setup when this model was created"

    request_dict = json.loads(request)

    query_dict = mii.utils.extract_query_dict(mii_config.task, request_dict)

    response = model.query(query_dict, **request_dict)

    time_taken = response.time_taken
    if not isinstance(response.response, str):
        response = list(response.response)
    return json.dumps({"responses": response, "time": time_taken})


### Auto-generated config will be appended below at run-time
