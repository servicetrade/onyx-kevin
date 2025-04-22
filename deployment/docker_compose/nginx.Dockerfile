FROM nginx:1.23.4-alpine

# Install build dependencies and curl
RUN apk add --no-cache \
    gcc \
    libc-dev \
    make \
    openssl-dev \
    pcre-dev \
    zlib-dev \
    linux-headers \
    curl \
    gnupg \
    libxslt-dev \
    gd-dev \
    geoip-dev \
    perl-dev \
    git

# Get nginx source
RUN wget http://nginx.org/download/nginx-1.23.4.tar.gz && \
    tar zxf nginx-1.23.4.tar.gz

# Download and unpack headers-more module
RUN wget https://github.com/openresty/headers-more-nginx-module/archive/v0.34.tar.gz && \
    tar zxf v0.34.tar.gz

# Build module
RUN cd nginx-1.23.4 && \
    ./configure --with-compat --add-dynamic-module=../headers-more-nginx-module-0.34 && \
    make modules

# Copy the compiled module to nginx modules directory
RUN mkdir -p /etc/nginx/modules && \
    cp nginx-1.23.4/objs/ngx_http_headers_more_filter_module.so /etc/nginx/modules/

# Clean up build dependencies BUT keep curl
RUN apk del gcc libc-dev make openssl-dev pcre-dev zlib-dev linux-headers gnupg libxslt-dev gd-dev geoip-dev perl-dev git && \
    rm -rf nginx-1.23.4* v0.34.tar.gz headers-more-nginx-module-0.34

# Make sure dos2unix is installed for the run script
RUN apk add --no-cache dos2unix curl
