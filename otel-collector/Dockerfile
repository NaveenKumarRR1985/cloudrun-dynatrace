FROM otel/opentelemetry-collector-contrib:latest

# Create non-root user for security
RUN addgroup -g 10001 otel && \
    adduser -D -u 10001 -G otel otel

# Copy configuration
COPY config.yaml /etc/otelcol-contrib/config.yaml

# Set ownership and permissions
RUN chown -R otel:otel /etc/otelcol-contrib && \
    chmod 644 /etc/otelcol-contrib/config.yaml

# Switch to non-root user
USER otel

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:13133/ || exit 1

# Expose ports
EXPOSE 4317 4318 8888 8889 13133

# Run collector
ENTRYPOINT ["/otelcol-contrib"]
CMD ["--config=/etc/otelcol-contrib/config.yaml"]