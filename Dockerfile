FROM public.ecr.aws/lambda/python:3.11
WORKDIR /var/task

COPY requirements_container.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Normalize runtime env for the app
ENV COURSE_DIR=/var/task/courses \
    DEFAULT_COURSE=decision

# Ensure the real V1666 Lambda handler is included
COPY lambda_handler_v1666_real.py .

# Copy FAISS index and metadata to the expected location
RUN set -eux; \
    mkdir -p /var/task/courses/decision; \
    if [ -f "vector_index.faiss" ]; then \
        echo "Found FAISS index at: vector_index.faiss"; \
        cp "vector_index.faiss" /var/task/courses/decision/vector_index.faiss; \
    else \
        echo "No vector_index.faiss found in context (this is OK if your app builds it at runtime)"; \
    fi; \
    if [ -f "metadata.json" ]; then \
        echo "Found metadata.json at: metadata.json"; \
        cp "metadata.json" /var/task/courses/decision/metadata.json; \
    else \
        echo "No metadata.json found in context (this is OK if your app builds it at runtime)"; \
    fi

CMD ["lambda_handler_v1666_real.handler"]
