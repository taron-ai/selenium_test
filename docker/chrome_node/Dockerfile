FROM selenium/standalone-chrome:latest

USER root
RUN apt-get update && apt-get install -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*     

# Set the user back to the default selenium user
USER seluser

EXPOSE 4444
