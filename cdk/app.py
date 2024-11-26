#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.cdk_stack import CdkStack


app = cdk.App()
CdkStack(app, "CdkStack",
    env=cdk.Environment(account="911167909001", region="us-east-2"),  # Usa tu cuenta y región
)


app.synth()
