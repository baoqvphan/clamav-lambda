# Stage 1: Build stage to install ClamAV and dependencies
FROM amazonlinux:2 AS build-stage

# Install ClamAV and dependencies
RUN yum update -y && \
    yum install -y clamav clamav-update tar gzip zip libtool-ltdl

# Install the required dependencies for ClamAV and freshclam
RUN mkdir -p /opt/clamav

# Copy ClamAV binaries
RUN cp /usr/bin/clamscan /opt/clamav/ && \
    cp /usr/bin/freshclam /opt/clamav/

# Copy necessary shared libraries
RUN cp /usr/lib64/libclamav.so.9 /opt/clamav/ && \
    cp /usr/lib64/libfreshclam.so.2 /opt/clamav/ && \
    cp /usr/lib64/libjson-c.so.2 /opt/clamav/ && \
    cp /usr/lib64/libltdl.so.7 /opt/clamav/ && \
    cp /usr/lib64/libz.so.1 /opt/clamav/ && \
    cp /usr/lib64/libc.so.6 /opt/clamav/

# Copy freshclam.conf
COPY freshclam.conf /opt/clamav/

# Make binaries executable
RUN chmod +x /opt/clamav/clamscan /opt/clamav/freshclam

# Make sure to copy all additional libraries required by ClamAV
RUN ldd /usr/bin/clamscan | grep "=>" | awk '{print $3}' | xargs -I '{}' cp '{}' /opt/clamav/

# Stage 2: Final stage with only necessary files
FROM amazonlinux:2 AS final-stage

# Set the environment variable for the install directory
ENV INSTALL_DIR=/opt/clamav

# Create the destination directory in final stage
RUN mkdir -p $INSTALL_DIR

# Copy necessary binaries and libraries from build stage
COPY --from=build-stage /opt/clamav/ $INSTALL_DIR/

# Zip binaries and dependencies into a single archive for later use
RUN cd /opt && zip -r9 /opt/clamav-scanner-layer.zip clamav
