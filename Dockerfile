# Use the Bitnami Python base image with Python 3.9
FROM bitnami/python:3.9

# Set the working directory inside the container
WORKDIR /app

# Install Node.js, Azure Functions Core Tools, and ICU library
RUN apt-get update && \
    apt-get install -y curl gnupg2 libicu-dev && \
    curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Copy the current directory contents into the container at /app
COPY . .

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Expose the port Azure Functions will run on
EXPOSE 8080

# Run the Azure Functions runtime
CMD ["func", "start", "--script-root", "."]
