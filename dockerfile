FROM public.ecr.aws/lambda/python:3.11

# Install PostgreSQL 15 client tools
RUN yum install -y \
    https://download.postgresql.org/pub/repos/yum/15/redhat/rhel-7-x86_64/postgresql15-libs-15.14-1PGDG.rhel7.x86_64.rpm \
    https://download.postgresql.org/pub/repos/yum/15/redhat/rhel-7-x86_64/postgresql15-15.14-1PGDG.rhel7.x86_64.rpm \
    https://download.postgresql.org/pub/repos/yum/15/redhat/rhel-7-x86_64/postgresql15-server-15.14-1PGDG.rhel7.x86_64.rpm \
    && yum clean all

# Copy your Lambda function code
COPY app.py ${LAMBDA_TASK_ROOT}

# Inform Lambda wich function is the entrypoint
CMD ["lambda_function.lambda_handler"]
