FROM public.ecr.aws/lambda/python:3.11
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Set environment variables
ENV COURSE_DIR=/var/task/courses \
    DEFAULT_COURSE=decision

# Command to run the Lambda handler
CMD ["lambda_function.lambda_handler"]
